"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { createClient } from "@/lib/supabase/client";
import type { SavedConfiguration, ConfigurationStatus } from "@drov/shared";

interface SaveConfigurationInput {
  boxModelId: string;
  name?: string;
  terminals: number;
  holesTop: { count: number; size: string };
  holesBottom: { count: number; size: string };
  holesLeft: { count: number; size: string };
  holesRight: { count: number; size: string };
  switchgear?: unknown[];
  coverElements?: unknown[];
  notes?: string;
}

export function useConfigurations() {
  const supabase = createClient();

  return useQuery({
    queryKey: ["configurations"],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("configurations")
        .select("*, box_models(name, series_id)")
        .order("created_at", { ascending: false });

      if (error) throw error;
      return data;
    },
  });
}

export function useConfiguration(id: string) {
  const supabase = createClient();

  return useQuery({
    queryKey: ["configuration", id],
    queryFn: async () => {
      const { data, error } = await supabase
        .from("configurations")
        .select("*, box_models(name, series_id)")
        .eq("id", id)
        .single();

      if (error) throw error;
      return data;
    },
    enabled: !!id,
  });
}

export function useSaveConfiguration() {
  const supabase = createClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: SaveConfigurationInput) => {
      const {
        data: { user },
      } = await supabase.auth.getUser();
      if (!user) throw new Error("Not authenticated");

      const { data, error } = await supabase
        .from("configurations")
        .insert({
          user_id: user.id,
          box_model_id: input.boxModelId,
          name: input.name || null,
          terminals: input.terminals,
          holes_top: input.holesTop,
          holes_bottom: input.holesBottom,
          holes_left: input.holesLeft,
          holes_right: input.holesRight,
          switchgear: input.switchgear || [],
          cover_elements: input.coverElements || [],
          notes: input.notes || null,
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
    },
  });
}

export function useUpdateConfigurationStatus() {
  const supabase = createClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      id,
      status,
    }: {
      id: string;
      status: ConfigurationStatus;
    }) => {
      const { data, error } = await supabase
        .from("configurations")
        .update({ status })
        .eq("id", id)
        .select()
        .single();

      if (error) throw error;
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
    },
  });
}

export function useDeleteConfiguration() {
  const supabase = createClient();
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: string) => {
      const { error } = await supabase
        .from("configurations")
        .delete()
        .eq("id", id);

      if (error) throw error;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["configurations"] });
    },
  });
}
