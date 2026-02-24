import { Outlet } from "react-router-dom";
import { MobileNav } from "./MobileNav";

export function DashboardLayout() {
  return (
    <div className="min-h-screen bg-background">
      <div className="pb-20">
        <Outlet />
      </div>
      <MobileNav />
    </div>
  );
}
