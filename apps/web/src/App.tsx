import { MantineProvider } from "@mantine/core";
import { Notifications } from "@mantine/notifications";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import "@mantine/core/styles.css";
import "@mantine/notifications/styles.css";

import { AppShellLayout } from "./components/layout/AppShellLayout";
import { DashboardPage } from "./features/dashboard/DashboardPage";
import { WorkflowEditorPage } from "./features/workflows/WorkflowEditorPage";
import { WorkflowsPage } from "./features/workflows/WorkflowsPage";

const queryClient = new QueryClient();

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <MantineProvider defaultColorScheme="dark">
        <Notifications />
        <BrowserRouter>
          <Routes>
            <Route element={<AppShellLayout />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/workflows" element={<WorkflowsPage />} />
              <Route path="/workflows/:workflowId" element={<WorkflowEditorPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </MantineProvider>
    </QueryClientProvider>
  );
}
