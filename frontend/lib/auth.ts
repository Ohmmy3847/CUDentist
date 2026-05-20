'use client'

export const saveToken = (token: string) => localStorage.setItem('token', token)
export const getToken = () => (typeof window !== 'undefined' ? localStorage.getItem('token') : null)
export const clearToken = () => localStorage.removeItem('token')
export const isLoggedIn = () => !!getToken()
