import React from 'react';
import Head from 'next/head';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  title?: string;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ 
  children, 
  title = "React Three Viz" 
}) => {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=0" />
        <meta name="description" content="High-performance 3D visualization using React and Three.js" />
      </Head>
      
      <main className="w-full h-screen overflow-hidden bg-gray-900 text-white relative">
        {/* Main Content Area */}
        <div className="absolute inset-0 z-0">
          {children}
        </div>

        {/* Overlay UI Layer (pointer-events-none allows clicking through to canvas where needed) */}
        <div className="absolute inset-0 z-10 pointer-events-none">
          {/* Header/Nav can go here */}
          <header className="absolute top-0 left-0 p-6 pointer-events-auto">
            <h1 className="text-2xl font-bold tracking-tighter">
              <span className="text-blue-400">R3F</span>
              <span className="text-white">_VIZ</span>
            </h1>
          </header>
          
          {/* Footer/Status can go here */}
          <footer className="absolute bottom-0 w-full p-4 text-center text-xs text-gray-600 pointer-events-auto">
            Interactive 3D Experience • Next.js + Three.js
          </footer>
        </div>
      </main>
    </>
  );
};