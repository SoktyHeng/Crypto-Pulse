import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/page-header";
import { ApiStatusPanel } from "@/components/system/api-status-panel";

export const metadata: Metadata = { title: "System status" };

export default function SystemPage() {
  return (
    <>
      <PageHeader
        title="System status"
        description="Read-only view of the API, database and data pipeline. No credentials or internal addresses are shown."
      />
      <ApiStatusPanel />
    </>
  );
}
