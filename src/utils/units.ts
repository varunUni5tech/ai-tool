/**
 * Unit conversion utilities for physics engine.
 */

export function degToRad(degrees: number): number {
  return (degrees * Math.PI) / 180.0;
}

export function radToDeg(radians: number): number {
  return (radians * 180.0) / Math.PI;
}

export function nmToMicrometers(nanometers: number): number {
  return nanometers / 1000.0;
}
