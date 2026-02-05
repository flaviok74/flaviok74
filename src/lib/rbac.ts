import { UserRole } from "@prisma/client";

export const rolePermissions: Record<UserRole, string[]> = {
  ADMIN: ["manage:users", "manage:quotes", "manage:catalogs", "view:audits"],
  OPERATOR: ["manage:quotes", "view:dashboard"],
  AUDITOR: ["view:audits", "view:dashboard"]
};

export function hasPermission(role: UserRole, permission: string) {
  return rolePermissions[role]?.includes(permission) ?? false;
}
