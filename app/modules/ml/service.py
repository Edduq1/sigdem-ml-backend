import os
from datetime import datetime

import joblib
import pandas as pd

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.modules.tramites.model import TramitePrioridad
from app.modules.tramites.service import get_tramite_by_id, create_history
from app.modules.ml.schema import TramiteMLClassifyRequest
from app.modules.users.model import User


MODEL_DIR = "ml_models"
MODEL_PATH = os.path.join(MODEL_DIR, "tramite_priority_rf.joblib")


def build_training_dataset():
    data = [
        ["Licencia de Funcionamiento", "Desarrollo Económico", 1, 2, False, False, "MEDIA"],
        ["Licencia de Funcionamiento", "Desarrollo Económico", 5, 3, True, False, "ALTA"],
        ["Certificado de Zonificación", "Desarrollo Urbano", 2, 1, False, False, "MEDIA"],
        ["Certificado de Zonificación", "Desarrollo Urbano", 7, 2, True, False, "ALTA"],
        ["Denuncia por riesgo estructural", "Defensa Civil", 1, 2, False, True, "CRITICA"],
        ["Inspección de Defensa Civil", "Defensa Civil", 2, 3, False, True, "CRITICA"],
        ["Reclamo ciudadano", "Atención al Ciudadano", 1, 1, False, False, "BAJA"],
        ["Reclamo ciudadano", "Atención al Ciudadano", 6, 1, True, False, "MEDIA"],
        ["Solicitud de información", "Secretaría General", 1, 1, False, False, "BAJA"],
        ["Solicitud de información", "Secretaría General", 4, 1, False, False, "BAJA"],
        ["Permiso de obra", "Desarrollo Urbano", 3, 4, False, False, "MEDIA"],
        ["Permiso de obra", "Desarrollo Urbano", 8, 5, True, False, "ALTA"],
        ["Riesgo sanitario", "Salud Pública", 1, 2, False, True, "CRITICA"],
        ["Fiscalización comercial", "Fiscalización", 3, 3, False, False, "MEDIA"],
        ["Fiscalización comercial", "Fiscalización", 6, 4, True, False, "ALTA"],
        ["Emergencia vecinal", "Defensa Civil", 0, 1, False, True, "CRITICA"],
        ["Queja administrativa", "Atención al Ciudadano", 2, 1, False, False, "BAJA"],
        ["Queja administrativa", "Atención al Ciudadano", 7, 2, True, False, "MEDIA"],
        ["Autorización municipal", "Administración", 2, 2, False, False, "MEDIA"],
        ["Autorización municipal", "Administración", 9, 3, True, False, "ALTA"],
    ]

    columns = [
        "tipo_tramite",
        "area_responsable",
        "dias_espera",
        "cantidad_documentos",
        "tiene_observaciones",
        "es_urgente",
        "prioridad"
    ]

    return pd.DataFrame(data, columns=columns)


def train_tramite_priority_model():
    os.makedirs(MODEL_DIR, exist_ok=True)

    df = build_training_dataset()

    X = df.drop(columns=["prioridad"])
    y = df["prioridad"]

    categorical_features = [
        "tipo_tramite",
        "area_responsable",
        "tiene_observaciones",
        "es_urgente"
    ]

    numeric_features = [
        "dias_espera",
        "cantidad_documentos"
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("numeric", "passthrough", numeric_features)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=120,
        random_state=42,
        max_depth=6
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    model_package = {
        "pipeline": pipeline,
        "accuracy": round(float(accuracy), 4),
        "total_samples": len(df),
        "labels": sorted(y.unique().tolist()),
        "trained_at": datetime.utcnow().isoformat()
    }

    joblib.dump(model_package, MODEL_PATH)

    return model_package


def load_or_train_model():
    if not os.path.exists(MODEL_PATH):
        return train_tramite_priority_model()

    return joblib.load(MODEL_PATH)


def classify_tramite_priority(data: TramiteMLClassifyRequest):
    model_package = load_or_train_model()
    pipeline = model_package["pipeline"]

    input_df = pd.DataFrame([{
        "tipo_tramite": data.tipo_tramite,
        "area_responsable": data.area_responsable,
        "dias_espera": data.dias_espera,
        "cantidad_documentos": data.cantidad_documentos,
        "tiene_observaciones": data.tiene_observaciones,
        "es_urgente": data.es_urgente
    }])

    prediction = pipeline.predict(input_df)[0]

    probabilities = pipeline.predict_proba(input_df)[0]
    confidence = round(float(max(probabilities)), 4)

    return {
        "prioridad": prediction,
        "confidence": confidence
    }


def detect_urgent_text(text: str) -> bool:
    text = text.lower()

    urgent_keywords = [
        "riesgo",
        "emergencia",
        "peligro",
        "derrumbe",
        "incendio",
        "salud",
        "defensa civil",
        "urgente"
    ]

    return any(keyword in text for keyword in urgent_keywords)


def predict_priority_for_existing_tramite(
    db: Session,
    tramite_id: int,
    current_user: User
):
    tramite = get_tramite_by_id(db, tramite_id)

    dias_espera = (datetime.utcnow() - tramite.fecha_registro).days

    text_to_analyze = f"{tramite.tipo_tramite} {tramite.descripcion} {tramite.area_responsable}"

    request_data = TramiteMLClassifyRequest(
        tipo_tramite=tramite.tipo_tramite,
        area_responsable=tramite.area_responsable,
        dias_espera=dias_espera,
        cantidad_documentos=1,
        tiene_observaciones=tramite.estado.value == "OBSERVADO",
        es_urgente=detect_urgent_text(text_to_analyze)
    )

    result = classify_tramite_priority(request_data)

    tramite.prioridad = TramitePrioridad(result["prioridad"])

    db.commit()
    db.refresh(tramite)

    create_history(
        db=db,
        tramite_id=tramite.id,
        usuario_id=current_user.id,
        accion="PRIORIDAD_PREDICHA_ML",
        comentario=f"Prioridad asignada por Random Forest: {result['prioridad']} con confianza {result['confidence']}"
    )

    return {
        "tramite_id": tramite.id,
        "codigo": tramite.codigo,
        "prioridad": result["prioridad"],
        "confidence": result["confidence"]
    }


def get_tramite_model_metrics():
    model_package = load_or_train_model()

    return {
        "model_name": "tramite_priority_rf",
        "algorithm": "Random Forest Classifier",
        "accuracy": model_package["accuracy"],
        "total_samples": model_package["total_samples"],
        "labels": model_package["labels"]
    }