import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    primaryColor: '#2563eb',
    lineColor: '#3f3f46',
    textColor: '#fafafa',
    mainBkg: '#18181b',
    nodeBorder: '#27272a',
  }
});

export default function MermaidChart({ chart }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current && chart) {
      ref.current.removeAttribute('data-processed');
      try {
        mermaid.contentLoaded();
      } catch (e) {
        console.error("Mermaid syntax error:", e);
      }
    }
  }, [chart]);

  return (
    <div className="mermaid flex justify-center bg-background/30 rounded-xl p-4 overflow-x-auto min-h-[200px]" ref={ref}>
      {chart}
    </div>
  );
}
