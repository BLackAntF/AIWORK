import jwt from 'jsonwebtoken'
import bcrypt from 'bcryptjs'

interface JWTPayload {
  userId: string
  email: string
  role: 'admin' | 'user'
}

export function generateToken(payload: JWTPayload): string {
  return jwt.sign(payload, process.env.JWT_SECRET!, {
    expiresIn: process.env.JWT_EXPIRES_IN || '7d'
  })
}

export function verifyToken(token: string): JWTPayload {
  try {
    return jwt.verify(token, process.env.JWT_SECRET!) as JWTPayload
  } catch {
    throw new Error('Invalid token')
  }
}

export async function hashPassword(password: string): Promise<string> {
  const salt = await bcrypt.genSalt(10)
  return bcrypt.hash(password, salt)
}

export async function comparePassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

export type Permission = 'read' | 'write' | 'delete' | 'admin'

export interface User {
  id: string
  role: 'admin' | 'moderator' | 'user'
}

const rolePermissions: Record<User['role'], Permission[]> = {
  admin: ['read', 'write', 'delete', 'admin'],
  moderator: ['read', 'write', 'delete'],
  user: ['read', 'write']
}

export function hasPermission(user: User, permission: Permission): boolean {
  return rolePermissions[user.role].includes(permission)
}
