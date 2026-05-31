import { SalonDetailView } from "@/components/SalonDetailView";

/**
 * Salon detail route. `params` is async in Next 16, so it is awaited here and
 * the resolved id is handed to the client-side detail view.
 */
export default async function SalonPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <SalonDetailView salonId={Number(id)} />;
}
