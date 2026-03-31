import { useEffect, useRef } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    primaryColor: '#2563eb',
    lineColor: '#6366f1',
    textColor: '#fafafa',
    mainBkg: '#18181b',
    nodeBorder: '#6366f1',
  }
});

export default function MermaidChart({ chart }) {
  const ref = useRef(null);
  const chartId = useRef(`chart-${Math.floor(Math.random() * 100000)}`);

  useEffect(() => {
    let isMounted = true;

    const renderChart = async () => {
      if (!ref.current || !chart) return;
      
      try {
        // Reset and show loader
        ref.current.innerHTML = '<div class="flex items-center justify-center py-20 opacity-30"><div class="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div></div>';
        
        // Render 
        const { svg } = await mermaid.render(chartId.current, chart);
        
        if (isMounted && ref.current) {
          ref.current.innerHTML = svg;
          const svgElement = ref.current.querySelector('svg');
          if (svgElement) {
            svgElement.style.width = '100%';
            svgElement.style.height = 'auto';
            svgElement.style.maxWidth = '1000px'; // Limit width for readability
          }
        }
      } catch (e) {
        console.error("Mermaid Chart Error:", e);
        if (isMounted && ref.current) {
          ref.current.innerHTML = `<div class="text-zinc-500 text-sm p-12 italic border border-dashed border-zinc-800 rounded-2xl w-full text-center">Finalizing architectural detail...</div>`;
        }
      }
    };

    renderChart();
    return () => { isMounted = false; };
  }, [chart]);

  return (
    <div 
      className="flex justify-center bg-background/30 rounded-3xl p-10 overflow-hidden w-full min-h-[500px]" 
      ref={ref} 
    />
  );
}
