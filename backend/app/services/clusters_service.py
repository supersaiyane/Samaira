from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.clusters import Cluster, ClusterResource
from app.models.resources import Resource
from app.schemas.clusters import ClusterCreate

async def list_clusters(db: AsyncSession):
    result = await db.execute(select(Cluster))
    return result.scalars().all()

async def get_cluster(db: AsyncSession, cluster_id: int):
    result = await db.execute(select(Cluster).where(Cluster.cluster_id == cluster_id))
    return result.scalars().first()

async def get_cluster_resources(db: AsyncSession, cluster_id: int):
    result = await db.execute(
        select(Resource)
        .join(ClusterResource, ClusterResource.resource_id == Resource.resource_id)
        .where(ClusterResource.cluster_id == cluster_id)
    )
    return result.scalars().all()

async def create_cluster(db: AsyncSession, cluster: ClusterCreate):
    new_cluster = Cluster(**cluster.dict())
    db.add(new_cluster)
    await db.commit()
    await db.refresh(new_cluster)
    return new_cluster

async def delete_cluster(db: AsyncSession, cluster_id: int):
    result = await db.execute(select(Cluster).where(Cluster.cluster_id == cluster_id))
    cluster = result.scalars().first()
    if not cluster:
        return None
    await db.delete(cluster)
    await db.commit()
    return cluster
