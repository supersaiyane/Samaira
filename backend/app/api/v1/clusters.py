from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.schemas.clusters import ClusterResponse, ClusterCreate, ClusterWithResources
from app.services import clusters_service

router = APIRouter()

@router.get("/", response_model=list[ClusterResponse])
async def list_clusters(db: AsyncSession = Depends(get_db)):
    return await clusters_service.list_clusters(db)

@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: int, db: AsyncSession = Depends(get_db)):
    cluster = await clusters_service.get_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.get("/{cluster_id}/resources", response_model=list[ClusterWithResources])
async def get_cluster_resources(cluster_id: int, db: AsyncSession = Depends(get_db)):
    return await clusters_service.get_cluster_resources(db, cluster_id)

@router.post("/", response_model=ClusterResponse)
async def create_cluster(cluster: ClusterCreate, db: AsyncSession = Depends(get_db)):
    return await clusters_service.create_cluster(db, cluster)

@router.delete("/{cluster_id}")
async def delete_cluster(cluster_id: int, db: AsyncSession = Depends(get_db)):
    cluster = await clusters_service.delete_cluster(db, cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return {"status": "deleted", "cluster_id": cluster_id}
