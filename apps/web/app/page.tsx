"use client";

import { useMemo, useState } from "react";

import {
  ALLOWED_EXTENSIONS,
  ASPECT_RATIOS,
  DEFAULT_IMAGE_COUNT,
  MAX_FILE_SIZE_MB,
  MAX_UPLOAD_COUNT,
} from "@cat-wallpaper/shared";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export default function Page() {
  const [files, setFiles] = useState<File[]>([]);
  const [prompt, setPrompt] = useState("");
  const [imageCount, setImageCount] = useState(DEFAULT_IMAGE_COUNT);
  const [aspectRatio, setAspectRatio] = useState(ASPECT_RATIOS[0]);
  const [images, setImages] = useState<string[]>([]);
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingImages, setLoadingImages] = useState(false);
  const [loadingVideo, setLoadingVideo] = useState(false);

  const fileSummary = useMemo(() => {
    if (!files.length) return "未选择文件";
    return `${files.length} / ${MAX_UPLOAD_COUNT} 已选`;
  }, [files]);

  const validateFiles = (selected: File[]) => {
    if (!selected.length) return "请至少选择一张图片。";
    if (selected.length > MAX_UPLOAD_COUNT) {
      return `最多只能上传 ${MAX_UPLOAD_COUNT} 张图片。`;
    }
    for (const file of selected) {
      const ext = file.name.split(".").pop()?.toLowerCase();
      if (!ext || !ALLOWED_EXTENSIONS.includes(ext as (typeof ALLOWED_EXTENSIONS)[number])) {
        return `不支持的格式：${file.name}`;
      }
      if (file.size > MAX_FILE_SIZE_MB * 1024 * 1024) {
        return `文件过大：${file.name}`;
      }
    }
    return null;
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(event.target.files ?? []);
    const validationError = validateFiles(selected);
    if (validationError) {
      setError(validationError);
      event.target.value = "";
      return;
    }
    setError(null);
    setFiles(selected);
  };

  const handleGenerateImages = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    const validationError = validateFiles(files);
    if (validationError) {
      setError(validationError);
      return;
    }
    setLoadingImages(true);
    setImages([]);
    setSelectedImage(null);
    setVideoUrl(null);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));
      formData.append("prompt", prompt);
      formData.append("image_count", String(imageCount));
      formData.append("aspect_ratio", aspectRatio);

      const response = await fetch(`${API_BASE}/api/generate-image`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || "生成图片失败。");
      }

      const payload = await response.json();
      setImages(payload.images ?? []);
      setJobId(payload.job_id ?? null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "生成图片失败。";
      setError(message);
    } finally {
      setLoadingImages(false);
    }
  };

  const handleGenerateVideo = async () => {
    if (!selectedImage || !jobId) {
      setError("请先选择一张图片。");
      return;
    }
    setError(null);
    setLoadingVideo(true);

    try {
      const response = await fetch(`${API_BASE}/api/generate-video`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          job_id: jobId,
          image_url: selectedImage,
          aspect_ratio: aspectRatio,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.detail || "生成视频失败。");
      }

      const payload = await response.json();
      setVideoUrl(payload.video_url ?? null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "生成视频失败。";
      setError(message);
    } finally {
      setLoadingVideo(false);
    }
  };

  return (
    <main className="app">
      <section className="panel">
        <header className="header">
          <p className="eyebrow">Cat Wallpaper Studio</p>
          <h1>把猫的记忆变成一段会动的壁纸</h1>
          <p className="subtitle">
            上传 1-5 张照片，生成 3-5 秒短视频。支持 16:9 / 9:16，适配桌面与手机壁纸。
          </p>
        </header>

        <form className="form" onSubmit={handleGenerateImages}>
          <div className="field">
            <label htmlFor="files">上传照片</label>
            <input
              id="files"
              type="file"
              accept={ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(",")}
              multiple
              onChange={handleFileChange}
            />
            <span className="hint">{fileSummary}</span>
          </div>

          <div className="grid">
            <div className="field">
              <label htmlFor="aspect">画幅比例</label>
              <select
                id="aspect"
                value={aspectRatio}
                onChange={(event) => setAspectRatio(event.target.value as (typeof ASPECT_RATIOS)[number])}
              >
                {ASPECT_RATIOS.map((ratio) => (
                  <option key={ratio} value={ratio}>
                    {ratio}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label htmlFor="count">生成图片数量</label>
              <input
                id="count"
                type="number"
                min={1}
                max={8}
                value={imageCount}
                onChange={(event) => {
                  const nextValue = Number(event.target.value);
                  setImageCount(Number.isFinite(nextValue) ? nextValue : 1);
                }}
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="prompt">提示词（可选）</label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="比如：柔和光影、电影感、梦境氛围…"
              rows={3}
            />
          </div>

          {error ? <p className="error">{error}</p> : null}

          <button className="primary" type="submit" disabled={loadingImages}>
            {loadingImages ? "生成中..." : "生成图片"}
          </button>
        </form>

        {images.length > 0 ? (
          <section className="results">
            <h2>选择一张生成视频</h2>
            <div className="image-grid">
              {images.map((url) => (
                <button
                  key={url}
                  className={url === selectedImage ? "image-card selected" : "image-card"}
                  type="button"
                  onClick={() => setSelectedImage(url)}
                >
                  <img src={`${API_BASE}${url}`} alt="Generated" />
                </button>
              ))}
            </div>

            <button className="secondary" type="button" onClick={handleGenerateVideo} disabled={loadingVideo}>
              {loadingVideo ? "生成视频中..." : "生成视频"}
            </button>
          </section>
        ) : null}

        {videoUrl ? (
          <section className="results">
            <h2>预览视频</h2>
            <video controls src={`${API_BASE}${videoUrl}`} />
          </section>
        ) : null}
      </section>
    </main>
  );
}
