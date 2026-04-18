import { Handle, Position, type NodeProps } from 'reactflow';
import jsPDF from 'jspdf';
import './index.css';

type CustomNodeData = {
  label: string;
  icon: string;
  color: string;
  agentName: string;
  downloadable?: boolean;
  pitchDeckId?: string;
};

const CustomNode = ({ data }: NodeProps<CustomNodeData>) => {
  // Parse the content to handle different formats (ideas, criticism, etc.)
  const lines = data.label.split('\n').filter(line => line.trim());
  
  // Check if it's a numbered list (ideas)
  const isNumberedList = lines.some(line => /^\d+\./.test(line.trim()));
  
  // Check if it has structured sections (critic format with emojis)
  const hasStructuredSections = data.label.includes('💪') || data.label.includes('⚠️') || data.label.includes('💡');
  
  // Check if it's the new critic format with IDEA blocks
  const hasSeparateIdeaBlocks = data.label.includes('⚡ IDEA');

  const handleDownloadPDF = () => {
    // Create PDF with jsPDF
    const doc = new jsPDF();
    
    // Add title
    doc.setFontSize(20);
    doc.setTextColor(245, 158, 11); // Orange color
    doc.text('PITCH DECK', 20, 20);
    
    // Add content
    doc.setFontSize(11);
    doc.setTextColor(0, 0, 0);
    
    const pageWidth = doc.internal.pageSize.getWidth();
    const margin = 20;
    const maxWidth = pageWidth - (margin * 2);
    
    // Split content into lines and add to PDF
    const contentLines = doc.splitTextToSize(data.label, maxWidth);
    let yPosition = 35;
    const lineHeight = 7;
    const pageHeight = doc.internal.pageSize.getHeight();
    
    contentLines.forEach((line: string) => {
      // Add new page if needed
      if (yPosition + lineHeight > pageHeight - margin) {
        doc.addPage();
        yPosition = margin;
      }
      
      doc.text(line, margin, yPosition);
      yPosition += lineHeight;
    });
    
    // Save the PDF
    doc.save('pitch-deck.pdf');
  };

  return (
    <div className="modern-node" style={{ borderTop: `4px solid ${data.color}` }}>
      <Handle type="target" position={Position.Top} isConnectable={false} />
      
      <div className="modern-node-header">
        <div className="node-icon-wrapper" style={{ background: `${data.color}20` }}>
          <span className="node-icon-large">{data.icon}</span>
        </div>
        <div className="node-header-text">
          <span className="node-agent-name">{data.agentName}</span>
          <span className="node-subtitle">AI Generated</span>
        </div>
      </div>

      <div className="modern-node-content">
        {isNumberedList ? (
          <div className="idea-list-modern">
            {lines.map((line, index) => {
              const match = line.match(/^(\d+)\.\s*(.+)/);
              if (match) {
                const ideaNumber = match[1];
                const ideaText = match[2];
                return (
                  <div key={index} className="idea-item-modern">
                    <div className="idea-number">{ideaNumber}</div>
                    <div className="idea-text">{ideaText}</div>
                  </div>
                );
              }
              return null;
            })}
          </div>
        ) : hasSeparateIdeaBlocks ? (
          <div className="critic-ideas-container">
            {data.label.split(/⚡ IDEA/).filter(block => block.trim()).map((block, blockIdx) => {
              // Skip empty blocks
              if (!block.trim()) return null;
              
              const lines = block.split('\n').filter(l => l.trim());
              // First line is the idea title/number
              const ideaTitle = lines[0] || '';
              
              // Parse sections within this idea block
              const strengthsStart = lines.findIndex(l => l.includes('💪'));
              const challengesStart = lines.findIndex(l => l.includes('⚠️'));
              const recommendationStart = lines.findIndex(l => l.includes('💡'));
              
              const strengths = strengthsStart !== -1 && challengesStart !== -1
                ? lines.slice(strengthsStart + 1, challengesStart).filter(l => l.trim() && l.startsWith('-'))
                : [];
              
              const challenges = challengesStart !== -1 && recommendationStart !== -1
                ? lines.slice(challengesStart + 1, recommendationStart).filter(l => l.trim() && l.startsWith('-'))
                : [];
              
              const recommendation = recommendationStart !== -1
                ? lines.slice(recommendationStart + 1).filter(l => l.trim() && !l.startsWith('-') && !l.includes('⚡')).join(' ')
                : '';
              
              return (
                <div key={blockIdx} className="critic-idea-block">
                  <div className="critic-idea-header">
                    ⚡ IDEA {ideaTitle}
                  </div>
                  
                  {strengths.length > 0 && (
                    <div className="critic-section section-strengths">
                      <div className="section-header">💪 Strengths</div>
                      <div className="section-body">
                        {strengths.map((item, i) => (
                          <div key={i} className="section-item">{item}</div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {challenges.length > 0 && (
                    <div className="critic-section section-challenges">
                      <div className="section-header">⚠️ Challenges</div>
                      <div className="section-body">
                        {challenges.map((item, i) => (
                          <div key={i} className="section-item">{item}</div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {recommendation && (
                    <div className="critic-section section-recommendation">
                      <div className="section-header">💡 Recommendation</div>
                      <div className="section-body">
                        <div className="section-item">{recommendation}</div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        ) : hasStructuredSections ? (
          <div className="structured-content">
            {data.label.split('\n\n').map((section, idx) => {
              const lines = section.split('\n');
              const header = lines[0];
              const items = lines.slice(1);
              
              let sectionClass = 'content-section';
              if (header.includes('')) sectionClass += ' section-strengths';
              else if (header.includes('')) sectionClass += ' section-challenges';
              else if (header.includes('')) sectionClass += ' section-recommendation';
              
              return (
                <div key={idx} className={sectionClass}>
                  <div className="section-header">{header}</div>
                  <div className="section-body">
                    {items.map((item, i) => (
                      item.trim() && <div key={i} className="section-item">{item}</div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="simple-content">
            {data.label}
          </div>
        )}
      </div>

      {/* Download button for pitch deck nodes */}
      {data.downloadable && (
        <div style={{ padding: '12px', borderTop: '1px solid #e5e7eb' }}>
          <button 
            onClick={handleDownloadPDF}
            style={{
              width: '100%',
              padding: '10px 16px',
              background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'all 0.2s ease'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-1px)';
              e.currentTarget.style.boxShadow = '0 4px 12px rgba(245, 158, 11, 0.3)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            <span>📥</span>
            Download Pitch Deck
          </button>
        </div>
      )}

      <Handle type="source" position={Position.Bottom} isConnectable={true} />
    </div>
  );
};

export default CustomNode;
