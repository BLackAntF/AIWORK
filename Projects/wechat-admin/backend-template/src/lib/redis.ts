import Redis from 'ioredis'

const REDIS_HOST = process.env.REDIS_HOST || 'localhost'
const REDIS_PORT = Number(process.env.REDIS_PORT) || 6379
const REDIS_PASSWORD = process.env.REDIS_PASSWORD || undefined

const redis = new Redis({
  host: REDIS_HOST,
  port: REDIS_PORT,
  password: REDIS_PASSWORD
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
    return
  }
  await redis.set(key, serialized)
}

export async function deleteCache(key: string): Promise<void> {
  await redis.del(key)
}

export async function existsCache(key: string): Promise<boolean> {
  const result = await redis.exists(key)
  return result === 1
}

export { redis }
