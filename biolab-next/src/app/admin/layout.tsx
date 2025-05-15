import { ReactNode } from "react";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex">
      <div className="flex-1 p-6">{children}</div>
    </div>
  );
}
