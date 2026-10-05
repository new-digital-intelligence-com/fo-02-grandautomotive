/** Voice tags such as [happy] or [laughs]: they steer the voice and are not meant to be read. */
const AUDIO_TAG = /\s*\[[a-z][a-z' -]{0,30}\]\s*/gi;

/**
 * Single digits with spaces, commas or dashes between them. Katerina writes phone numbers this way
 * ("2 1 4, 4 4 4, 4 6 4 0") so the voice reads them digit by digit.
 */
const SPACED_DIGITS = /(?<!\d|\d[.,])\d(?![.,]?\d)(?:[  ]*[,-]?[  ]*\d(?![.,]?\d))+/g; // "3 4,5" is not a digit run

/** A price Katerina writes without a thousands separator ("20900 ευρώ"), so the voice reads it as one number. */
const PRICE = /(?<![\d.,])\d{4,7}(?=[  ]?(?:ευρώ|€|euros?\b))/gi;

/**
 * Text as the transcript shows it: a number spelled out digit by digit shown whole (2144444640), prices with the
 * usual separator (20.900 ευρώ, 20,900 euros), and no voice tags.
 */
export function transcriptText(text: string): string {
  return text
    .replace(AUDIO_TAG, " ")
    .replace(SPACED_DIGITS, (run) => {
      const digits = run.replace(/\D/g, "");
      return digits.length >= 4 ? digits : run; // "1, 2, 3" stays a short list
    })
    .replace(PRICE, (digits: string, offset: number, whole: string) => {
      const english = /^[  ]?euro/i.test(whole.slice(offset + digits.length));
      return digits.replace(/\B(?=(\d{3})+(?!\d))/g, english ? "," : ".");
    })
    .replace(/[  ]{2,}/g, " ")
    .trim();
}
