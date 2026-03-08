import { useEffect, useState } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { getAdminToken, validateAdminToken, removeAdminToken } from "@/lib/api";
import { Loader2 } from "lucide-react";

interface AdminGuardProps {
  children: React.ReactNode;
}

export function AdminGuard({ children }: AdminGuardProps) {
  const location = useLocation();
  const [isValidating, setIsValidating] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = getAdminToken();
      
      if (!token) {
        setIsAuthenticated(false);
        setIsValidating(false);
        return;
      }

      // Validate token by making a request to dashboard
      try {
        const isValid = await validateAdminToken();
        setIsAuthenticated(isValid);
      } catch (error) {
        removeAdminToken();
        setIsAuthenticated(false);
      } finally {
        setIsValidating(false);
      }
    };

    checkAuth();
  }, [location.pathname]);

  if (isValidating) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/admin/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}
