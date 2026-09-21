import { z } from 'zod';

export const PrismParametersSchema = z.object({
  apex_angle: z.number({
    required_error: "apex_angle is required",
    invalid_type_error: "apex_angle must be a number (e.g. 60.0)"
  }).min(1, "apex_angle must be > 0°").max(179, "apex_angle must be < 180°"),

  incident_angle: z.number({
    required_error: "incident_angle is required",
    invalid_type_error: "incident_angle must be a number (e.g. 30.0)"
  }).min(0, "incident_angle must be >= 0°").max(89.9, "incident_angle must be < 90°"),

  cauchy_b: z.number({
    required_error: "cauchy_b is required",
    invalid_type_error: "cauchy_b must be a number (e.g. 1.5)"
  }).min(1.0, "cauchy_b must be >= 1.0"),

  cauchy_c: z.number({
    required_error: "cauchy_c is required",
    invalid_type_error: "cauchy_c must be a number (e.g. 0.004)"
  }).min(0, "cauchy_c must be >= 0"),

  wavelengths_nm: z.array(
    z.number({ invalid_type_error: "Wavelength must be a number in nanometers" })
      .min(200, "Wavelength must be >= 200 nm")
      .max(2000, "Wavelength must be <= 2000 nm")
  ).min(1, "At least one wavelength is required in wavelengths_nm array"),
});

export const SimulationSpecSchema = z.object({
  simulation_schema_version: z.string().default("1.0"),
  simulation_type: z.string({ required_error: "simulation_type is required" }),
  domain: z.string({ required_error: "domain is required" }),
  parameters: PrismParametersSchema,
  visualization: z.record(z.any()).optional(),
  educational: z.record(z.any()).optional(),
});

export type SimulationSpecType = z.infer<typeof SimulationSpecSchema>;
