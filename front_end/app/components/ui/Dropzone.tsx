import React, { useCallback, useRef, useState } from "react";

type DropzoneRenderProps = {
  isDragging: boolean;
  openFileDialog: () => void;
};

type DropzoneProps = {
  onFiles: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
  className?: string;
  children: (props: DropzoneRenderProps) => React.ReactNode;
};

export default function Dropzone({
  onFiles,
  accept = "image/*,.jpg,.jpeg,.png",
  multiple = true,
  className,
  children,
}: DropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const openFileDialog = useCallback(() => {
    inputRef.current?.click();
  }, []);

  const emitFiles = useCallback(
    (list: FileList | File[]) => {
      const files = Array.from(list);
      onFiles(files);
    },
    [onFiles]
  );

  const onDrop = useCallback(
    (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragging(false);
      if (e.dataTransfer?.files?.length) emitFiles(e.dataTransfer.files);
    },
    [emitFiles]
  );

  const onDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  }, []);

  const onDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const onChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files?.length) emitFiles(e.target.files);
      // allow same file selection again
      e.target.value = "";
    },
    [emitFiles]
  );

  return (
    <div
      className={className}
      onDrop={onDrop}
      onDragOver={onDragOver}
      onDragEnter={onDragEnter}
      onDragLeave={onDragLeave}
      role="button"
      aria-label="File upload dropzone"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openFileDialog();
        }
      }}
    >
      {children({ isDragging, openFileDialog })}
      <input
        ref={inputRef}
        type="file"
        multiple={multiple}
        accept={accept}
        onChange={onChange}
        className="hidden"
      />
    </div>
  );
}
