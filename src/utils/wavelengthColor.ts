/**
 * Converts a spectral wavelength in nanometers (380nm - 750nm) to approximate RGB HEX color.
 */
export function wavelengthToHexColor(wavelengthNm: number): string {
  let r = 0;
  let g = 0;
  let b = 0;

  if (wavelengthNm >= 380 && wavelengthNm < 440) {
    r = -(wavelengthNm - 440) / (440 - 380);
    g = 0.0;
    b = 1.0;
  } else if (wavelengthNm >= 440 && wavelengthNm < 490) {
    r = 0.0;
    g = (wavelengthNm - 440) / (490 - 440);
    b = 1.0;
  } else if (wavelengthNm >= 490 && wavelengthNm < 510) {
    r = 0.0;
    g = 1.0;
    b = -(wavelengthNm - 510) / (510 - 490);
  } else if (wavelengthNm >= 510 && wavelengthNm < 580) {
    r = (wavelengthNm - 510) / (580 - 510);
    g = 1.0;
    b = 0.0;
  } else if (wavelengthNm >= 580 && wavelengthNm < 645) {
    r = 1.0;
    g = -(wavelengthNm - 645) / (645 - 580);
    b = 0.0;
  } else if (wavelengthNm >= 645 && wavelengthNm <= 750) {
    r = 1.0;
    g = 0.0;
    b = 0.0;
  } else {
    return '#ffffff';
  }

  // Intensity factor falloff near vision limits
  let factor = 1.0;
  if (wavelengthNm >= 380 && wavelengthNm < 420) {
    factor = 0.3 + (0.7 * (wavelengthNm - 380)) / (420 - 380);
  } else if (wavelengthNm >= 700 && wavelengthNm <= 750) {
    factor = 0.3 + (0.7 * (750 - wavelengthNm)) / (750 - 700);
  }

  const red = Math.round(Math.min(1.0, Math.max(0.0, r * factor)) * 255);
  const green = Math.round(Math.min(1.0, Math.max(0.0, g * factor)) * 255);
  const blue = Math.round(Math.min(1.0, Math.max(0.0, b * factor)) * 255);

  const toHex = (c: number) => c.toString(16).padStart(2, '0');
  return `#${toHex(red)}${toHex(green)}${toHex(blue)}`;
}

export function getSpectralName(wavelengthNm: number): string {
  if (wavelengthNm >= 620) return 'Red';
  if (wavelengthNm >= 590) return 'Orange';
  if (wavelengthNm >= 570) return 'Yellow';
  if (wavelengthNm >= 495) return 'Green';
  if (wavelengthNm >= 450) return 'Blue';
  if (wavelengthNm >= 400) return 'Violet';
  return 'UV / Near IR';
}
