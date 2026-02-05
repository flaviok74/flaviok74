import { UserRole } from "@prisma/client";

export const rolePermissions: Record<UserRole, string[]> = {
  ADMIN: ["manage:users", "manage:quotes", "manage:catalogs", "view:audits"],
  ANALYST: ["manage:quotes", "view:dashboard"],
  VIEWER: ["view:audits", "view:dashboard"]
};

export function hasPermission(role: UserRole, permission: string) {
  return rolePermissions[role]?.includes(permission) ?? false;
}
