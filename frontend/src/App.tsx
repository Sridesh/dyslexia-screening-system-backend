import { ThemeProvider, CssBaseline } from "@mui/material";
import { BrowserRouter, Routes, Route } from "react-router";
import theme from "./theme/theme";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import ChildrenList from "./pages/ChildrenList";
import ChildDetail from "./pages/ChildDetail";
import TestSession from "./pages/TestSession";
import TestResults from "./pages/TestResults";
import NotFound from "./pages/NotFound";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/children" element={<ChildrenList />} />
            <Route path="/children/:childId" element={<ChildDetail />} />
            <Route path="/children/:childId/test" element={<TestSession />} />
            <Route path="/tests/:testId/results" element={<TestResults />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
}

export default App;
