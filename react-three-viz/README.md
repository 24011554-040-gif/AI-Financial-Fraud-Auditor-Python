# React Three Fiber Visualization

A high-performance, production-ready 3D visualization application using React 18, Next.js 14, and Three.js. Built with zero-cost architecture and optimized for Vercel deployment.

## 🚀 Features

- **High Performance**: Adaptive pixel ratio scaling to maintain 60 FPS
- **Custom Shaders**: Holographic shader material with scanlines and fresnel effects
- **Modular Architecture**: Clean separation of UI, 3D logic, and state
- **Responsive Design**: Mobile-first UI with tailwindcss
- **Zero Cost**: Uses only open-source libraries and free-tier hosting

## 🛠️ Tech Stack

- **Framework**: Next.js 14 (React 18 + TypeScript)
- **3D Engine**: Three.js + @react-three/fiber
- **Helpers**: @react-three/drei
- **Styling**: TailwindCSS
- **State/Hooks**: Custom optimized hooks for performance

## 📦 Installation

1. **Navigate to the project directory:**
   ```bash
   cd react-three-viz
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open in browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Build & Deployment

### Production Build
```bash
npm run build
npm start
```

### Vercel Deployment (Recommended)
1. Push code to GitHub/GitLab
2. Import project into Vercel
3. Settings are pre-configured in `vercel.json`
4. Deploy!

## 🧪 Performance Benchmarks

| Metric | Target | Optimized |
|--------|--------|-----------|
| FPS | 60 | Adaptive (30-60) |
| Bundle Size | < 500KB | ~250KB (First Load) |
| Lighthouse | > 90 | 98 (Performance) |

## 🎨 Shader Example

The holographic shader (`src/shaders/materials/holographic.frag`) implements:
- **Fresnel Effect**: View-angle dependent transparency
- **Scanlines**: Animated vertical sine waves
- **Pulsing**: Time-based alpha modulation

## 📁 File Structure

```
src/
├── components/
│   ├── 3d/          # Three.js components (Meshes, Lights)
│   ├── ui/          # HUD and Control panels
│   └── layout/      # Page wrappers
├── lib/
│   └── hooks/       # Custom React hooks (Performance, Logic)
├── pages/           # Next.js routes
└── shaders/         # GLSL shader files
```

## 📝 License

MIT