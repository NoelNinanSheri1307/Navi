import React, { useRef, useEffect } from "react";

const CustomBackground = ({ type, color }) => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let animationFrameId;

    let elements = [];
    let frame = 0;
    const count = 50;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      init();
    };

    const init = () => {
      elements = [];
      for (let i = 0; i < count; i++) {
        elements.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: Math.random() * 0.4 - 0.2,
          vy: Math.random() * 0.4 - 0.2,
          size: Math.random() * 3 + 1,
          id: i,
          angle: Math.random() * Math.PI * 2
        });
      }
    };

    const render = () => {
        // Core background fill
        ctx.fillStyle = "#050506";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        frame++;

        elements.forEach((e, i) => {
            e.x += e.vx; e.y += e.vy;
            if (e.x < 0) e.x = canvas.width; if (e.x > canvas.width) e.x = 0;
            if (e.y < 0) e.y = canvas.height; if (e.y > canvas.height) e.y = 0;

            switch(type) {
                case 'GA': // Genetic DNA Double Helix
                    const helixX = canvas.width / 2;
                    const helixSpacing = 200;
                    const y = (i * (canvas.height / count)) + (frame % canvas.height);
                    const drawY = y % canvas.height;

                    const helixOffset = Math.sin(drawY * 0.01) * 60;
                    
                    // Strand 1
                    ctx.fillStyle = `${color}44`;
                    ctx.beginPath(); ctx.arc(helixX + helixOffset, drawY, 3, 0, Math.PI * 2); ctx.fill();
                    
                    // Strand 2
                    ctx.fillStyle = `${color}88`;
                    ctx.beginPath(); ctx.arc(helixX - helixOffset, drawY, 3, 0, Math.PI * 2); ctx.fill();
                    
                    // Connecting Rungs
                    if (i % 3 === 0) {
                        ctx.strokeStyle = `${color}22`;
                        ctx.beginPath(); ctx.moveTo(helixX + helixOffset, drawY); ctx.lineTo(helixX - helixOffset, drawY); 
                        ctx.stroke();
                    }
                    break;

                case 'GWO': // White/Silver Mesh Pack
                    elements.forEach((other, j) => {
                        if (i === j) return;
                        const d = Math.sqrt((e.x-other.x)**2 + (e.y-other.y)**2);
                        if (d < 180) {
                            ctx.beginPath();
                            ctx.moveTo(e.x, e.y); ctx.lineTo(other.x, other.y);
                            ctx.strokeStyle = `rgba(255,255,255,${(1 - d/180) * 0.08})`;
                            ctx.lineWidth = 1;
                            ctx.stroke();
                        }
                    });
                    ctx.fillStyle = "rgba(255,255,255,0.1)";
                    ctx.fillRect(e.x-1, e.y-1, 3, 3);
                    break;

                case 'PSO': // Electric Blue Swarm
                    const swarmCenterX = canvas.width / 2;
                    const swarmCenterY = canvas.height / 2;
                    e.vx += (swarmCenterX - e.x) * 0.00001;
                    e.vy += (swarmCenterY - e.y) * 0.00001;
                    ctx.beginPath();
                    ctx.arc(e.x, e.y, e.size, 0, Math.PI * 2);
                    ctx.fillStyle = `${color}66`;
                    ctx.shadowBlur = 10; ctx.shadowColor = color;
                    ctx.fill(); ctx.shadowBlur = 0;
                    break;

                case 'ACO': // Amber Pheromone Network
                    elements.forEach((other, j) => {
                        if (j % 5 !== 0) return;
                        const d = Math.sqrt((e.x-other.x)**2 + (e.y-other.y)**2);
                        if (d < 300) {
                            ctx.beginPath();
                            ctx.moveTo(e.x, e.y); ctx.lineTo(other.x, other.y);
                            ctx.strokeStyle = `${color}${Math.floor((1 - d/300) * 20).toString(16).padStart(2, '0')}`;
                            ctx.stroke();
                        }
                    });
                    ctx.fillStyle = `${color}44`;
                    ctx.beginPath(); ctx.rect(e.x-2, e.y-2, 4, 4); ctx.fill();
                    break;

                case 'SA': // Molten Heatmap
                    const pulse = Math.sin(frame * 0.02 + e.id) * 0.5 + 0.5;
                    const g = ctx.createRadialGradient(e.x, e.y, 0, e.x, e.y, e.size * 50 * pulse);
                    g.addColorStop(0, `${color}22`); g.addColorStop(1, 'transparent');
                    ctx.fillStyle = g;
                    ctx.beginPath(); ctx.arc(e.x, e.y, e.size * 50 * pulse, 0, Math.PI * 2); ctx.fill();
                    break;

                case 'DE': // Industrial Vector Fields
                    const angle = Math.atan2(e.y - canvas.height/2, e.x - canvas.width/2) + frame * 0.01;
                    ctx.beginPath();
                    ctx.moveTo(e.x, e.y);
                    ctx.lineTo(e.x + Math.cos(angle) * 30, e.y + Math.sin(angle) * 30);
                    ctx.strokeStyle = `${color}33`;
                    ctx.stroke();
                    break;
                
                case 'HOME': // Generic Neural Static for Entry
                    ctx.beginPath();
                    ctx.arc(e.x, e.y, e.size * 0.5, 0, Math.PI * 2);
                    ctx.fillStyle = "rgba(255,255,255,0.05)";
                    ctx.fill();
                    if (i % 10 === 0) {
                        ctx.beginPath();
                        ctx.moveTo(e.x, e.y);
                        ctx.lineTo(e.x + 100, e.y + e.vy * 200);
                        ctx.strokeStyle = "rgba(255,255,255,0.02)";
                        ctx.stroke();
                    }
                    break;
                
                case 'COMPARE': // Multi-colored Neural Grid 
                    const colors = ["#10b981", "#3b82f6", "#94a3b8", "#8b5cf6", "#f59e0b", "#f43f5e"];
                    const c = colors[i % colors.length];
                    const op = Math.sin(frame * 0.01 + i) * 0.1 + 0.1;
                    
                    ctx.beginPath();
                    ctx.moveTo(e.x, 0); ctx.lineTo(e.x, canvas.height);
                    ctx.strokeStyle = `${c}${Math.floor(op * 255).toString(16).padStart(2, '0')}`;
                    ctx.stroke();
                    
                    ctx.beginPath();
                    ctx.moveTo(0, e.y); ctx.lineTo(canvas.width, e.y);
                    ctx.stroke();
                    break;
            }
        });

        animationFrameId = requestAnimationFrame(render);
    };

    resize();
    render();
    window.addEventListener('resize', resize);
    return () => {
        cancelAnimationFrame(animationFrameId);
        window.removeEventListener('resize', resize);
    };
  }, [type, color]);

  return (
    <canvas 
        ref={canvasRef} 
        className="fixed inset-0 -z-50 pointer-events-none" 
    />
  );
};

export default CustomBackground;
