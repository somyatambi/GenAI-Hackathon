import { useReactFlow } from 'reactflow';
import { useState, useEffect } from 'react';

const ZoomSlider = () => {
  const { zoomIn, zoomOut, setViewport, getViewport } = useReactFlow();
  const [zoom, setZoom] = useState(1);

  useEffect(() => {
    const interval = setInterval(() => {
      const viewport = getViewport();
      setZoom(viewport.zoom);
    }, 100);
    return () => clearInterval(interval);
  }, [getViewport]);

  const handleZoomChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newZoom = parseFloat(e.target.value);
    setZoom(newZoom);
    const viewport = getViewport();
    setViewport({ ...viewport, zoom: newZoom });
  };

  return (
    <div className="zoom-slider-container">
      <button 
        className="zoom-btn" 
        onClick={() => zoomOut()}
        title="Zoom Out"
      >
        −
      </button>
      <input
        type="range"
        min="0.2"
        max="2"
        step="0.1"
        value={zoom}
        onChange={handleZoomChange}
        className="zoom-slider"
      />
      <button 
        className="zoom-btn" 
        onClick={() => zoomIn()}
        title="Zoom In"
      >
        +
      </button>
      <span className="zoom-label">{Math.round(zoom * 100)}%</span>
    </div>
  );
};

export default ZoomSlider;
