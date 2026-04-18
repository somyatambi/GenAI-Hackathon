import { useState, useEffect } from 'react';
import type { Node, Edge } from 'reactflow';

interface Canvas {
  id: string;
  name: string;
  nodes: Node[];
  edges: Edge[];
  createdAt: number;
  lastModified: number;
}

interface WorkspacePanelProps {
  currentNodes: Node[];
  currentEdges: Edge[];
  onLoadCanvas: (nodes: Node[], edges: Edge[]) => void;
  onNewCanvas: () => void;
}

const WorkspacePanel = ({ currentNodes, currentEdges, onLoadCanvas, onNewCanvas }: WorkspacePanelProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [canvases, setCanvases] = useState<Canvas[]>([]);
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [canvasName, setCanvasName] = useState('');
  const [activeCanvasId, setActiveCanvasId] = useState<string | null>(null);
  const [editingCanvasId, setEditingCanvasId] = useState<string | null>(null);
  const [editCanvasName, setEditCanvasName] = useState('');

  // Load canvases from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('cognitive-canvas-workspaces');
    if (saved) {
      setCanvases(JSON.parse(saved));
    }
  }, []);

  // Save canvases to localStorage whenever they change
  useEffect(() => {
    if (canvases.length > 0) {
      localStorage.setItem('cognitive-canvas-workspaces', JSON.stringify(canvases));
    }
  }, [canvases]);

  const handleSaveCanvas = () => {
    if (!canvasName.trim()) return;

    const now = Date.now();
    const newCanvas: Canvas = {
      id: `canvas-${now}`,
      name: canvasName.trim(),
      nodes: currentNodes,
      edges: currentEdges,
      createdAt: now,
      lastModified: now,
    };

    setCanvases([newCanvas, ...canvases]);
    setActiveCanvasId(newCanvas.id);
    setCanvasName('');
    setSaveDialogOpen(false);
  };

  const handleLoadCanvas = (canvas: Canvas) => {
    onLoadCanvas(canvas.nodes, canvas.edges);
    setActiveCanvasId(canvas.id);
    setIsOpen(false);
  };

  const handleDeleteCanvas = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this canvas?')) {
      setCanvases(canvases.filter(c => c.id !== id));
      if (activeCanvasId === id) {
        setActiveCanvasId(null);
      }
    }
  };

  const handleStartEdit = (canvas: Canvas, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCanvasId(canvas.id);
    setEditCanvasName(canvas.name);
  };

  const handleSaveEdit = (canvasId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!editCanvasName.trim()) return;

    setCanvases(canvases.map(c => 
      c.id === canvasId 
        ? { ...c, name: editCanvasName.trim(), lastModified: Date.now() }
        : c
    ));
    setEditingCanvasId(null);
    setEditCanvasName('');
  };

  const handleCancelEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCanvasId(null);
    setEditCanvasName('');
  };

  const handleNewCanvas = () => {
    if (currentNodes.length > 1 || currentEdges.length > 0) {
      if (confirm('Start a new canvas? Your current work will be lost unless you save it.')) {
        onNewCanvas();
        setActiveCanvasId(null);
        setIsOpen(false);
      }
    } else {
      onNewCanvas();
      setActiveCanvasId(null);
      setIsOpen(false);
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          top: '80px',
          left: isOpen ? '320px' : '20px',
          zIndex: 1000,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          border: 'none',
          borderRadius: '12px',
          padding: '12px 20px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
          transition: 'all 0.3s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
        }}
      >
        <span>{isOpen ? '✕' : '📁'}</span>
        {isOpen ? 'Close' : 'Workspace'}
      </button>

      {/* Side Panel */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: isOpen ? 0 : '-320px',
          width: '320px',
          height: '100vh',
          background: 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
          boxShadow: isOpen ? '4px 0 20px rgba(0, 0, 0, 0.3)' : 'none',
          transition: 'left 0.3s ease',
          zIndex: 999,
          display: 'flex',
          flexDirection: 'column',
          color: 'white',
        }}
      >
        {/* Header */}
        <div style={{ padding: '24px', borderBottom: '1px solid rgba(255, 255, 255, 0.1)' }}>
          <h2 style={{ margin: 0, fontSize: '24px', fontWeight: '700', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            🎨 My Workspace
          </h2>
          <p style={{ margin: '8px 0 0', fontSize: '13px', color: 'rgba(255, 255, 255, 0.6)' }}>
            {canvases.length} saved canvas{canvases.length !== 1 ? 'es' : ''}
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <button
            onClick={handleNewCanvas}
            style={{
              background: 'linear-gradient(135deg, #2dd4bf 0%, #14b8a6 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              padding: '14px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.02)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(45, 212, 191, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <span style={{ fontSize: '18px' }}>✨</span>
            New Canvas
          </button>

          <button
            onClick={() => setSaveDialogOpen(true)}
            style={{
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              padding: '14px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'scale(1.02)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(245, 158, 11, 0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'scale(1)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <span style={{ fontSize: '18px' }}>💾</span>
            Save Current Canvas
          </button>
        </div>

        {/* Canvases List */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '0 16px 16px' }}>
          <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'rgba(255, 255, 255, 0.7)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Saved Canvases
          </h3>
          
          {canvases.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              padding: '40px 20px', 
              color: 'rgba(255, 255, 255, 0.4)',
              fontSize: '14px',
            }}>
              <div style={{ fontSize: '48px', marginBottom: '12px' }}>📭</div>
              <p>No saved canvases yet</p>
              <p style={{ fontSize: '12px', marginTop: '8px' }}>Create your first masterpiece!</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {canvases.map((canvas) => (
                <div
                  key={canvas.id}
                  onClick={() => handleLoadCanvas(canvas)}
                  style={{
                    background: activeCanvasId === canvas.id 
                      ? 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)'
                      : 'rgba(255, 255, 255, 0.05)',
                    borderRadius: '12px',
                    padding: '16px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    border: activeCanvasId === canvas.id ? '2px solid rgba(102, 126, 234, 0.5)' : '2px solid transparent',
                  }}
                  onMouseEnter={(e) => {
                    if (activeCanvasId !== canvas.id) {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
                      e.currentTarget.style.transform = 'translateX(4px)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (activeCanvasId !== canvas.id) {
                      e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                      e.currentTarget.style.transform = 'translateX(0)';
                    }
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div style={{ flex: 1 }}>
                      {editingCanvasId === canvas.id ? (
                        <div onClick={(e) => e.stopPropagation()}>
                          <input
                            type="text"
                            value={editCanvasName}
                            onChange={(e) => setEditCanvasName(e.target.value)}
                            onKeyPress={(e) => {
                              if (e.key === 'Enter') handleSaveEdit(canvas.id, e as any);
                              if (e.key === 'Escape') handleCancelEdit(e as any);
                            }}
                            autoFocus
                            style={{
                              width: '100%',
                              padding: '6px 8px',
                              fontSize: '15px',
                              border: '2px solid rgba(102, 126, 234, 0.5)',
                              borderRadius: '6px',
                              background: 'rgba(255, 255, 255, 0.1)',
                              color: 'white',
                              marginBottom: '4px',
                              outline: 'none',
                            }}
                          />
                          <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                            <button
                              onClick={(e) => handleSaveEdit(canvas.id, e)}
                              style={{
                                padding: '4px 12px',
                                fontSize: '11px',
                                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                                color: 'white',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontWeight: '600',
                              }}
                            >
                              ✓ Save
                            </button>
                            <button
                              onClick={(e) => handleCancelEdit(e)}
                              style={{
                                padding: '4px 12px',
                                fontSize: '11px',
                                background: 'rgba(255, 255, 255, 0.1)',
                                color: 'rgba(255, 255, 255, 0.7)',
                                border: '1px solid rgba(255, 255, 255, 0.2)',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontWeight: '600',
                              }}
                            >
                              ✕ Cancel
                            </button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div style={{ fontSize: '15px', fontWeight: '600', marginBottom: '4px', color: 'white' }}>
                            {canvas.name}
                          </div>
                          <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)' }}>
                            {formatDate(canvas.lastModified)}
                          </div>
                        </>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '6px' }}>
                      {editingCanvasId !== canvas.id && (
                        <button
                          onClick={(e) => handleStartEdit(canvas, e)}
                          style={{
                            background: 'rgba(102, 126, 234, 0.2)',
                            color: '#667eea',
                            border: 'none',
                            borderRadius: '6px',
                            padding: '6px 10px',
                            fontSize: '12px',
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.background = 'rgba(102, 126, 234, 0.3)';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.background = 'rgba(102, 126, 234, 0.2)';
                          }}
                        >
                          ✏️
                        </button>
                      )}
                      <button
                        onClick={(e) => handleDeleteCanvas(canvas.id, e)}
                        style={{
                          background: 'rgba(239, 68, 68, 0.2)',
                          color: '#ef4444',
                          border: 'none',
                          borderRadius: '6px',
                          padding: '6px 10px',
                          fontSize: '12px',
                          cursor: 'pointer',
                          transition: 'all 0.2s ease',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.3)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.2)';
                        }}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'rgba(255, 255, 255, 0.6)' }}>
                    <span>📊 {canvas.nodes.length} nodes</span>
                    <span>🔗 {canvas.edges.length} edges</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Save Dialog Modal */}
      {saveDialogOpen && (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
            backdropFilter: 'blur(4px)',
          }}
          onClick={() => setSaveDialogOpen(false)}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: 'linear-gradient(180deg, #1a1a2e 0%, #16213e 100%)',
              borderRadius: '16px',
              padding: '32px',
              maxWidth: '400px',
              width: '90%',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
            }}
          >
            <h3 style={{ margin: '0 0 8px', fontSize: '22px', color: 'white', fontWeight: '700' }}>
              💾 Save Canvas
            </h3>
            <p style={{ margin: '0 0 24px', fontSize: '14px', color: 'rgba(255, 255, 255, 0.6)' }}>
              Give your canvas a memorable name
            </p>
            
            <input
              type="text"
              value={canvasName}
              onChange={(e) => setCanvasName(e.target.value)}
              placeholder="e.g., SaaS Startup Ideas"
              autoFocus
              onKeyPress={(e) => e.key === 'Enter' && handleSaveCanvas()}
              style={{
                width: '100%',
                padding: '14px',
                fontSize: '15px',
                border: '2px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '10px',
                background: 'rgba(255, 255, 255, 0.05)',
                color: 'white',
                marginBottom: '24px',
                outline: 'none',
                transition: 'all 0.2s ease',
              }}
              onFocus={(e) => {
                e.currentTarget.style.borderColor = 'rgba(102, 126, 234, 0.5)';
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.08)';
              }}
              onBlur={(e) => {
                e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
              }}
            />

            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setSaveDialogOpen(false)}
                style={{
                  flex: 1,
                  padding: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  border: '2px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px',
                  background: 'transparent',
                  color: 'rgba(255, 255, 255, 0.7)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'transparent';
                  e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCanvas}
                disabled={!canvasName.trim()}
                style={{
                  flex: 1,
                  padding: '12px',
                  fontSize: '14px',
                  fontWeight: '600',
                  border: 'none',
                  borderRadius: '10px',
                  background: canvasName.trim() 
                    ? 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                    : 'rgba(255, 255, 255, 0.1)',
                  color: canvasName.trim() ? 'white' : 'rgba(255, 255, 255, 0.3)',
                  cursor: canvasName.trim() ? 'pointer' : 'not-allowed',
                  transition: 'all 0.2s ease',
                }}
                onMouseEnter={(e) => {
                  if (canvasName.trim()) {
                    e.currentTarget.style.transform = 'scale(1.02)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(245, 158, 11, 0.4)';
                  }
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'scale(1)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default WorkspacePanel;
