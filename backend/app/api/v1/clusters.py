from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.core.db import get_db
from app.models.clusters import Cluster, ClusterResource
from app.models.resources import Resource
from app.schemas.clusters import ClusterResponse, ClusterCreate, ClusterWithResources

router = APIRouter()

@router.get("/", response_model=list[ClusterResponse])
async def list_clusters(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cluster))
    clusters = result.scalars().all()
    return clusters

@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(cluster_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cluster).where(Cluster.cluster_id == cluster_id))
    cluster = result.scalars().first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return cluster

@router.get("/{cluster_id}/resources", response_model=ClusterWithResources)
async def get_cluster_resources(cluster_id: int, db: AsyncSession = Depends(get_db)):
    # Check if cluster exists
    result = await db.execute(select(Cluster).where(Cluster.cluster_id == cluster_id))
    cluster = result.scalars().first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")

    # Fetch linked resources
    result = await db.execute(
        select(Resource)
        .join(ClusterResource, ClusterResource.resource_id == Resource.resource_id)
        .where(ClusterResource.cluster_id == cluster_id)
    )
    resources = result.scalars().all()
    return {"cluster": cluster, "resources": resources}

@router.post("/", response_model=ClusterResponse)
async def create_cluster(cluster: ClusterCreate, db: AsyncSession = Depends(get_db)):
    new_cluster = Cluster(**cluster.dict())
    db.add(new_cluster)
    await db.commit()
    await db.refresh(new_cluster)
    return new_cluster

@router.delete("/{cluster_id}")
async def delete_cluster(cluster_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cluster).where(Cluster.cluster_id == cluster_id))
    cluster = result.scalars().first()
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    await db.delete(cluster)
    await db.commit()
    return {"status": "deleted", "cluster_id": cluster_id}
