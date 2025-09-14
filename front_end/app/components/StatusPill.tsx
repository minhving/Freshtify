interface StatusPillProps {
  status: string;
  className?: string;
}

export function StatusPill({ status, className = "" }: StatusPillProps) {
  const getStatusStyles = (status: string) => {
    switch (status) {
      case "High":
        return "bg-highStock-bg text-highStock-text";
      case "Medium":
        return "bg-mediumStock-bg text-mediumStock-text";
      case "Low":
        return "bg-lowStock-bg text-lowStock-text";
      default:
        return "bg-gray-500 text-white";
    }
  };

  return (
    <span
      className={`w-16 px-2 py-1 rounded-full text-xs font-medium text-center inline-block ${getStatusStyles(
        status
      )} ${className}`}
    >
      {status}
    </span>
  );
}
