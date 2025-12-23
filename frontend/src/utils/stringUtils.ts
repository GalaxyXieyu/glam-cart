
/**
 * Formats a string by replacing placeholders with arguments
 * Example: formatString("Hello {0}", "World") => "Hello World"
 */
export const formatString = (format: string, ...args: any[]): string => {
  return format.replace(/{(\d+)}/g, (match, number) => {
    return typeof args[number] !== 'undefined' ? args[number] : match;
  });
};
