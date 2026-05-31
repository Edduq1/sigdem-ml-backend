from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.modules.cvs.model import CV
from app.modules.cvs.service import get_cv_by_id
from app.modules.hr.service import get_job_by_id


def clean_text(text: str) -> str:
    """
    Limpieza básica de texto para análisis NLP.
    """
    return text.lower().strip()


def calculate_cv_job_match(db: Session, cv_id: int, job_id: int):
    """
    Calcula la compatibilidad entre un CV y una convocatoria laboral.
    Usa TF-IDF + similitud coseno.
    """
    cv = get_cv_by_id(db, cv_id)
    job = get_job_by_id(db, job_id)

    if not cv.texto_extraido or cv.texto_procesado != "SI":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El CV todavía no tiene texto extraído. Primero ejecuta /api/cvs/{cv_id}/extract"
        )

    cv_text = clean_text(cv.texto_extraido)

    job_text = clean_text(
        f"{job.titulo} {job.descripcion} {job.requisitos} {job.area}"
    )

    documents = [
        cv_text,
        job_text
    ]

    vectorizer = TfidfVectorizer(
        stop_words=None,
        ngram_range=(1, 2)
    )

    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    compatibility = round(float(similarity * 100), 2)

    if compatibility >= 75:
        resultado = "Candidato altamente compatible"
    elif compatibility >= 50:
        resultado = "Candidato compatible"
    elif compatibility >= 30:
        resultado = "Candidato parcialmente compatible"
    else:
        resultado = "Candidato con baja compatibilidad"

    return {
        "cv_id": cv.id,
        "job_id": job.id,
        "candidato": cv.nombre_candidato,
        "convocatoria": job.titulo,
        "compatibilidad": compatibility,
        "resultado": resultado
    }


def generate_cv_ranking(db: Session, job_id: int):
    """
    Genera un ranking de CVs asociados a una convocatoria.
    """
    job = get_job_by_id(db, job_id)

    cvs = db.query(CV).filter(CV.job_id == job_id).all()

    if not cvs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existen CVs asociados a esta convocatoria"
        )

    ranking = []

    for cv in cvs:
        if cv.texto_extraido and cv.texto_procesado == "SI":
            result = calculate_cv_job_match(db, cv.id, job.id)

            ranking.append({
                "cv_id": cv.id,
                "candidato": cv.nombre_candidato,
                "correo": cv.correo_candidato,
                "telefono": cv.telefono_candidato,
                "compatibilidad": result["compatibilidad"],
                "resultado": result["resultado"]
            })

    if not ranking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los CVs asociados aún no tienen texto extraído"
        )

    ranking = sorted(
        ranking,
        key=lambda item: item["compatibilidad"],
        reverse=True
    )

    return {
        "job_id": job.id,
        "convocatoria": job.titulo,
        "total_candidatos": len(ranking),
        "ranking": ranking
    }