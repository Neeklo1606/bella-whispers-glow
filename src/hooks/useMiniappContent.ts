import { useQuery } from "@tanstack/react-query";
import { getMiniappContent } from "@/lib/api";

/** Load MiniApp content from API. Public endpoint, no auth. */
export function useMiniappContent() {
  return useQuery({
    queryKey: ["miniapp-content"],
    queryFn: getMiniappContent,
    staleTime: 60_000, // 1 min
  });
}
