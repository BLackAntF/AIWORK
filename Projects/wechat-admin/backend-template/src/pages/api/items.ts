import { NextApiResponse } from 'next'
import { z } from 'zod'
import { ResultSetHeader } from 'mysql2'
import { withAuth, AuthenticatedRequest } from '@/middleware'
import { query, queryOne } from '@/lib/db'
import { getCache, setCache, deleteCache } from '@/lib/redis'
import { errorHandler, ApiError } from '@/lib/error'

const CACHE_TTL = 300
const ALLOWED_METHODS = ['GET', 'POST', 'PUT', 'DELETE']

const createItemSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  description: z.string().max(1000).optional()
})

const updateItemSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255).optional(),
  description: z.string().max(1000).optional()
})

interface ItemRow {
  id: number
  name: string
  description: string | null
  created_at: Date
}

function getItemCacheKey(id: string | string[] | undefined): string {
  return `item:${id}`
}

async function fetchItemById(id: string): Promise<ItemRow | null> {
  return queryOne<ItemRow>(
    'SELECT id, name, description, created_at FROM items WHERE id = ?',
    [id]
  )
}

async function fetchAllItems(): Promise<ItemRow[]> {
  return query<ItemRow>(
    'SELECT id, name, description, created_at FROM items ORDER BY created_at DESC'
  )
}

async function getCachedOrFetch<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  const cached = await getCache<T>(key)
  if (cached) return cached
  const data = await fetcher()
  await setCache(key, data, CACHE_TTL)
  return data
}

async function handleGetItemById(id: string, res: NextApiResponse) {
  const cacheKey = getItemCacheKey(id)
  const item = await getCachedOrFetch(cacheKey, () => fetchItemById(id))

  if (!item) {
    throw new ApiError(404, 'Item not found')
  }

  res.status(200).json({ success: true, data: item })
}

async function handleGetAllItems(res: NextApiResponse) {
  const items = await getCachedOrFetch('items:all', fetchAllItems)
  res.status(200).json({ success: true, data: items })
}

async function handleGetItems(req: AuthenticatedRequest, res: NextApiResponse) {
  const { id } = req.query
  if (id) {
    return handleGetItemById(String(id), res)
  }
  return handleGetAllItems(res)
}

async function handleCreateItem(req: AuthenticatedRequest, res: NextApiResponse) {
  const { name, description } = createItemSchema.parse(req.body)
  const userId = req.user?.userId

  const [result] = await query<ResultSetHeader>(
    'INSERT INTO items (name, description, created_by) VALUES (?, ?, ?)',
    [name, description || null, userId]
  )

  await deleteCache('items:all')

  res.status(201).json({
    success: true,
    data: { id: result.insertId, name, description }
  })
}

async function handleUpdateItem(req: AuthenticatedRequest, res: NextApiResponse) {
  const { id } = req.query
  if (!id) {
    throw new ApiError(400, 'Item ID is required')
  }

  const { name, description } = updateItemSchema.parse(req.body)

  const [result] = await query<ResultSetHeader>(
    'UPDATE items SET name = COALESCE(?, name), description = COALESCE(?, description) WHERE id = ?',
    [name || null, description !== undefined ? description : null, id]
  )

  if (result.affectedRows === 0) {
    throw new ApiError(404, 'Item not found')
  }

  await deleteCache(`item:${id}`)
  await deleteCache('items:all')

  res.status(200).json({
    success: true,
    data: { id, name, description }
  })
}

async function handleDeleteItem(req: AuthenticatedRequest, res: NextApiResponse) {
  const { id } = req.query
  if (!id) {
    throw new ApiError(400, 'Item ID is required')
  }

  const [result] = await query<ResultSetHeader>('DELETE FROM items WHERE id = ?', [id])

  if (result.affectedRows === 0) {
    throw new ApiError(404, 'Item not found')
  }

  await deleteCache(`item:${id}`)
  await deleteCache('items:all')

  res.status(200).json({ success: true, message: 'Item deleted successfully' })
}

async function handler(req: AuthenticatedRequest, res: NextApiResponse) {
  try {
    const { method } = req

    switch (method) {
      case 'GET':
        return handleGetItems(req, res)
      case 'POST':
        return handleCreateItem(req, res)
      case 'PUT':
        return handleUpdateItem(req, res)
      case 'DELETE':
        return handleDeleteItem(req, res)
      default:
        res.setHeader('Allow', ALLOWED_METHODS)
        throw new ApiError(405, `Method ${method} Not Allowed`)
    }
  } catch (error) {
    errorHandler(error, res)
  }
}

export default withAuth(handler)
