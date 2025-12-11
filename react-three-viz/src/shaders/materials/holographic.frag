uniform float uTime;
uniform vec3 uColor;

varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vPosition;

void main() {
    // Basic holographic effect
    vec3 viewDirection = normalize(cameraPosition - vPosition);
    float fresnel = dot(viewDirection, vNormal);
    fresnel = pow(fresnel, 2.0);

    // Scanline effect
    float scanline = sin(vPosition.y * 10.0 + uTime * 2.0);
    scanline = smoothstep(0.0, 1.0, scanline);

    // Combine effects
    float alpha = fresnel + scanline * 0.1;
    
    // Add pulsing glow
    float glow = sin(uTime) * 0.2 + 0.8;
    
    vec3 finalColor = uColor * glow;

    gl_FragColor = vec4(finalColor, alpha);
}