export class AppSettings {
  public static BACKEND_HOST =
    process.env.NEXT_PUBLIC_BACKEND_HOST ?? 'http://localhost:9999'
  public static FRONTEND_HOST =
    process.env.NEXT_PUBLIC_FRONTEND_HOST ?? 'http://localhost:3000'
}
