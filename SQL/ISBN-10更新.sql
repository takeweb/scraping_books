SELECT * FROM public.books
ORDER BY id ASC;

UPDATE public.books SET isbn_10 = '4062639246' WHERE id = 21;
UPDATE public.books SET isbn_10 = '4062645602' WHERE id = 22;
UPDATE public.books SET isbn_10 = '4062646145' WHERE id = 23;