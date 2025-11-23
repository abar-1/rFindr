SELECT *
FROM public.match_professor_embeddings(
  '[0.01, 0.02, ...]'::vector, 5
);