import React, { Suspense, lazy } from \"react\";
const HeavyMarkdownRenderer = lazy(() => import(\"./HeavyMarkdownRenderer\"));

export const LazyMarkdownViewer = ({ content }) => (
  <Suspense fallback={<div className="loading-skeleton">Loading markdown...</div>}>
    <HeavyMarkdownRenderer content={content} />
  </Suspense>
);
