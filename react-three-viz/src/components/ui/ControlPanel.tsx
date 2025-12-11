import React from 'react';

interface ControlPanelProps {
  onColorChange: (color: string) => void;
  onSpeedChange: (speed: number) => void;
  onDistortionChange: (distortion: number) => void;
}

export const ControlPanel: React.FC<ControlPanelProps> = ({ 
  onColorChange, 
  onSpeedChange, 
  onDistortionChange 
}) => {
  return (
    <div className="absolute top-4 right-4 p-4 bg-black/50 backdrop-blur-md rounded-lg border border-white/10 text-white w-64 z-10 transition-all hover:bg-black/60">
      <h3 className="text-lg font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
        Holo Controls
      </h3>
      
      <div className="space-y-4">
        {/* Color Control */}
        <div className="space-y-2">
          <label className="text-sm text-gray-300 flex justify-between">
            <span>Hologram Color</span>
          </label>
          <div className="flex gap-2">
            {['#00ff88', '#00ccff', '#ff00ff', '#ffaa00'].map((color) => (
              <button
                key={color}
                onClick={() => onColorChange(color)}
                className="w-8 h-8 rounded-full border-2 border-white/20 transition-transform hover:scale-110 focus:ring-2 ring-white/50"
                style={{ backgroundColor: color }}
                aria-label={`Select color ${color}`}
              />
            ))}
          </div>
        </div>

        {/* Speed Control */}
        <div className="space-y-2">
          <label htmlFor="speed-range" className="text-sm text-gray-300 flex justify-between">
            <span>Rotation Speed</span>
          </label>
          <input
            id="speed-range"
            type="range"
            min="0"
            max="2"
            step="0.1"
            defaultValue="0.5"
            onChange={(e) => onSpeedChange(parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-blue-500 hover:accent-blue-400"
          />
        </div>

        {/* Distortion Control */}
        <div className="space-y-2">
          <label htmlFor="distortion-range" className="text-sm text-gray-300 flex justify-between">
            <span>Glitch Intensity</span>
          </label>
          <input
            id="distortion-range"
            type="range"
            min="0"
            max="1"
            step="0.05"
            defaultValue="0"
            onChange={(e) => onDistortionChange(parseFloat(e.target.value))}
            className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-purple-500 hover:accent-purple-400"
          />
        </div>
      </div>
      
      <div className="mt-6 text-xs text-gray-500 text-center border-t border-white/10 pt-2">
        Powered by React Three Fiber
      </div>
    </div>
  );
};