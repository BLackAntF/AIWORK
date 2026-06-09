import { NextApiResponse } from 'next'
import { withAuth, AuthenticatedRequest } from '@/middleware'
import { query, queryOne } from '@/lib/db'
import { getCache, setCache, deleteCache } from '@/lib/redis'

async function handler(req: AuthenticatedRequest, res: NextApiResponse) {
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
      res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE'])
      return res.status(405).json({ error: `Method ${method} Not Allowed` })
  }
}

async function handleGetItems(req: AuthenticatedRequest, res: NextApiResponse) {
  const { id } = req.query

  if (id) {
    const cacheKey = `item:${id}`
    const cachedItem = await getCache(cacheKey)

    if (cachedItem) {
      return res.status(200).json({ success: true, data: cachedItem })
    }

    const item = await queryOne('SELECT id, name, description, created_at FROM items WHERE id = ?', [id])

    if (!item) {
      return res.status(404).json({ error: 'Item not found' })
    }

    await setCache(cacheKey, item, 300)

    return res.status(200).json({ success: true, data: item })
  }

  const cacheKey = 'items:all'
  const cachedItems = await getCache(cacheKey)

  if (cachedItems) {
    return res.status(200).json({ success: true, data: cachedItems })
  }

  const items = await query('SELECT id, name, description, created_at FROM items ORDER BY created_at DESC')

  await setCache(cacheKey, items, 300)

  res.status(200).json({ success: true, data: items })
}

async function handleCreateItem(req: AuthenticatedRequest, res: NextApiResponse) {
  const { name, description } = req.body

  if (!name) {
    return res.status(400).json({ error: 'Name is required' })
  }

  const [result] = await query(
    'INSERT INTO items (name, description, created_by) VALUES (?, ?, ?)',
    [name, description, req.user?.userId]
  )

  const itemId = (result as any).insertId

  await deleteCache('items:all')

  res.status(201).json({
    success: true,
    data: {
      id: itemId,
      name,
      description
    }
  })
}

async function handleUpdateItem(req: AuthenticatedRequest, res: NextApiResponse) {
  const { id } = req.query
  const { name, description } = req.body

  if (!id) {
    return res.status(400).json({ error: 'Item ID is required' })
  }

  const [result] = await query(
    'UPDATE items SET name = ?, description = ? WHERE id = ?',
    [name, description, id]
  )

  if ((result as any).affectedRows === 0) {
    return res.status(404).json({ error: 'Item not found' })
  }

  await deleteCache(`item:${id}`)
  await deleteCache('items:all')

  res.status(200).json({
    success: true,
    data: {
      id,
      name,
      description
    }
  })
}

async function handleDeleteItem(req: AuthenticatedRequest, res: NextApiResponse) {
  const { id } = req.query

  if (!id) {
    return res.status(400).json({ error: 'Item ID is required' })
  }

  const [result] = await query('DELETE FROM items WHERE id = ?', [id])

  if ((result as any).affectedRows === 0) {
    return res.status(404).json({ error: 'Item not found' })
  }

  await deleteCache(`item:${id}`)
  await deleteCache('items:all')

  res.status(200).json({ success: true, message: 'Item deleted successfully' })
}

export default withAuth(handler)
