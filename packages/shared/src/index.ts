export const MAX_UPLOAD_COUNT = 5;
export const MAX_FILE_SIZE_MB = 20;
export const ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"] as const;
export const DEFAULT_IMAGE_COUNT = 4;
export const ASPECT_RATIOS = ["16:9", "9:16"] as const;
export type AspectRatio = (typeof ASPECT_RATIOS)[number];
