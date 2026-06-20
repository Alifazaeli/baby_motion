/**
 * Route-level auth guard for the Content Studio.
 * The /login route is public; everything else requires a valid studio_access_token.
 * Role enforcement (super_admin / content_admin) is handled server-side by IsStudioUser.
 */
import { NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = ["/login", "/studio/api"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (PUBLIC_PATHS.some((p) => pathname.startsWith(p))) return NextResponse.next();

  const token = request.cookies.get("studio_access_token")?.value
    ?? request.headers.get("authorization")?.replace("Bearer ", "");

  if (!token) {
    const loginUrl = request.nextUrl.clone();
    loginUrl.pathname = "/login";
    loginUrl.searchParams.set("next", pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
