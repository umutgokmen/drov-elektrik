"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import type { User, Session } from "@supabase/supabase-js";
import { createClient } from "@/lib/supabase/client";

interface UserProfile {
  id: string;
  fullName: string;
  company: string;
  role: "user" | "admin" | "engineer";
}

interface AuthState {
  user: User | null;
  session: Session | null;
  profile: UserProfile | null;
  loading: boolean;
}

export function useAuth() {
  const router = useRouter();
  const supabase = createClient();
  const [state, setState] = useState<AuthState>({
    user: null,
    session: null,
    profile: null,
    loading: true,
  });

  useEffect(() => {
    const getSession = async () => {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      if (session?.user) {
        const { data: profile } = await supabase
          .from("profiles")
          .select("id, full_name, company, role")
          .eq("id", session.user.id)
          .single();

        setState({
          user: session.user,
          session,
          profile: profile
            ? {
                id: profile.id,
                fullName: profile.full_name ?? "",
                company: profile.company ?? "",
                role: profile.role ?? "user",
              }
            : null,
          loading: false,
        });
      } else {
        setState({ user: null, session: null, profile: null, loading: false });
      }
    };

    getSession();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (_event, session) => {
      if (session?.user) {
        const { data: profile } = await supabase
          .from("profiles")
          .select("id, full_name, company, role")
          .eq("id", session.user.id)
          .single();

        setState({
          user: session.user,
          session,
          profile: profile
            ? {
                id: profile.id,
                fullName: profile.full_name ?? "",
                company: profile.company ?? "",
                role: profile.role ?? "user",
              }
            : null,
          loading: false,
        });
      } else {
        setState({ user: null, session: null, profile: null, loading: false });
      }
    });

    return () => subscription.unsubscribe();
  }, [supabase]);

  const signOut = useCallback(async () => {
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }, [supabase, router]);

  return { ...state, signOut };
}
