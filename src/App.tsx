import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import Pricing from "./pages/Pricing";
import Login from "./pages/Login";
import Consent from "./pages/Consent";
import Profile from "./pages/Profile";
import SubscriptionManagement from "./pages/SubscriptionManagement";
import AdminDashboard from "./pages/AdminDashboard";
import AdminUsers from "./pages/AdminUsers";
import AdminSubscriptions from "./pages/AdminSubscriptions";
import AdminSettings from "./pages/AdminSettings";
import AdminContent from "./pages/AdminContent";
import AdminLogin from "./pages/AdminLogin";
import { AdminLayout } from "./components/layout/AdminLayout";
import { AdminGuard } from "./components/AdminGuard";
import { BottomNav } from "./components/layout/BottomNav";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<><Index /><BottomNav /></>} />
          <Route path="/pricing" element={<><Pricing /><BottomNav /></>} />
          <Route path="/login" element={<><Login /><BottomNav /></>} />
          <Route path="/consent" element={<><Consent /><BottomNav /></>} />

          {/* Profile = dashboard + profile combined */}
          <Route path="/dashboard/profile" element={<><Profile /><BottomNav /></>} />
          <Route path="/dashboard/subscription" element={<><SubscriptionManagement /><BottomNav /></>} />
          
          {/* Redirects for old routes */}
          <Route path="/dashboard" element={<Navigate to="/dashboard/profile" replace />} />
          <Route path="/dashboard/feed" element={<Navigate to="/" replace />} />
          <Route path="/dashboard/favorites" element={<Navigate to="/dashboard/profile" replace />} />

          <Route path="/admin/login" element={<AdminLogin />} />
          <Route
            path="/admin"
            element={
              <AdminGuard>
                <AdminLayout />
              </AdminGuard>
            }
          >
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="subscriptions" element={<AdminSubscriptions />} />
            <Route path="settings" element={<AdminSettings />} />
            <Route path="content" element={<AdminContent />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
