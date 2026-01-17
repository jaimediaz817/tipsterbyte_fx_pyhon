# TODO: tb-task-hu-scheduler-01: implementar el servicio scheduler_service.py
from core.scheduler.jobs_loader import register_jobs
from core.scheduler import scheduler
from fastapi.responses import JSONResponse
import pytz

def get_status():
    if not scheduler.running:
        return JSONResponse(status_code=503, content={"error": "Scheduler no está activo"})
    
    jobs = scheduler.get_jobs()
    return {
        "status": "running",
        "active_jobs": len(jobs),
        "jobs": [
            {
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.astimezone(pytz.timezone("America/Bogota")).strftime("%Y-%m-%d %H:%M:%S") if job.next_run_time else None,
                "status": "paused" if job.next_run_time is None else "scheduled",
                "func": job.func_ref,                
            }
            for job in jobs
        ]
    }

def pause_all():
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.pause_job(job.id)
    return {"message": f"{len(jobs)} jobs pausados correctamente"}

def resume_all():
    jobs = scheduler.get_jobs()
    for job in jobs:
        scheduler.resume_job(job.id)
    return {"message": f"{len(jobs)} jobs reanudados correctamente"}

def pause(job_id: str):
    scheduler.pause_job(job_id)
    return {"message": f"Job {job_id} pausado correctamente"}

def resume(job_id: str):
    scheduler.resume_job(job_id)
    return {"message": f"Job {job_id} reanudado correctamente"}

def reload_jobs():
    scheduler.remove_all_jobs()
    register_jobs(scheduler)
    return {"message": "Jobs recargados desde base de datos exitosamente"}
