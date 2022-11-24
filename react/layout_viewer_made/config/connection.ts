const BACKEND_HOST =
  process.env.NEXT_PUBLIC_BACKEND_HOST ?? 'http://localhost:9999'
const FRONTEND_HOST =
  process.env.NEXT_PUBLIC_FRONTEND_HOST ?? 'http://localhost:3000'
const DASH_HOST = process.env.NEXT_PUBLIC_DASH_HOST ?? 'http://localhost:12345'

export { BACKEND_HOST, FRONTEND_HOST, DASH_HOST }
