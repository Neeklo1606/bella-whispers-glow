import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Pricing from "./pages/Pricing";
import Login from "./pages/Login";
import Consent from "./pages/Consent";
import Dashboard from "./pages/Dashboard";
import Feed from "./pages/Feed";
import Favorites from "./pages/Favorites";
import Profile from "./pages/Profile";
import SubscriptionManagement from "./pages/SubscriptionManagement";
import AdminDashboard from "./pages/AdminDashboard";
import AdminUsers from "./pages/AdminUsers";
import { AdminLayout } from "./components/layout/AdminLayout";
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
          {/* Marketing */}
          <Route path="/" element={<><Index /><BottomNav /></>} />
          <Route path="/pricing" element={<><Pricing /><BottomNav /></>} />

          {/* Auth */}
          <Route path="/login" element={<><Login /><BottomNav /></>} />
          <Route path="/consent" element={<><Consent /><BottomNav /></>} />

          {/* Dashboard pages — with bottom nav */}
          <Route path="/dashboard" element={<><Dashboard /><BottomNav /></>} />
          <Route path="/dashboard/feed" element={<><Feed /><BottomNav /></>} />
          <Route path="/dashboard/favorites" element={<><Favorites /><BottomNav /></>} />
          <Route path="/dashboard/profile" element={<><Profile /><BottomNav /></>} />
          <Route path="/dashboard/subscription" element={<><SubscriptionManagement /><BottomNav /></>} />

          {/* Admin */}
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
