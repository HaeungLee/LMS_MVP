import { useState, useEffect } from 'react';

function Timer({ onTimeUpdate }) {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setSeconds(prev => {
        const newTime = prev + 1;
        if (onTimeUpdate) {
          onTimeUpdate(newTime);
        }
        return newTime;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [onTimeUpdate]);

  const formatTime = (totalSeconds) => {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const secs = totalSeconds % 60;

    if (hours > 0) {
      return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const containerStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '8px 16px',
    backgroundColor: '#f0f9ff',
    border: '1px solid #0ea5e9',
    borderRadius: '20px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#0c4a6e'
  };

  return (
    <div style={containerStyle}>
      <span>⏱️</span>
      <span>경과 시간: {formatTime(seconds)}</span>
    </div>
  );
}

export default Timer;
