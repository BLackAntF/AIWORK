import Redis from 'ioredis'

const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: Number(process.env.REDIS_PORT) || 6379,
  password: process.env.REDIS_PASSWORD || undefined
})

export async function getCache<T>(key: string): Promise<T | null> {
  const value = await redis.get(key)
  if (!value) return null
  try {
    return JSON.parse(value)
  } catch {
    return value as T
  }
}

export async function setCache<T>(key: string, value: T, ttl?: number): Promise<void> {
  const serialized = typeof value === 'string' ? value : JSON.stringify(value)
  if (ttl) {
    await redis.set(key, serialized, 'EX', ttl)
  } else {
    await redis.set(key, serialized)
  }
}

export async function deleteCache(key: string): Promise<void> {
  await redis.del(key)
}

export async function existsCache(key: string): Promise<boolean> {
  const result = await redis.exists(key)
  return result === 1
}

export { redis }
