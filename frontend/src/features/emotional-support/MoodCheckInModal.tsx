/**
 * 기분 체크인 모달
 * 
 * 학습 전후의 감정 상태를 기록하는 UI
 */
import { useState } from 'react';
import { X } from 'lucide-react';
import toast from 'react-hot-toast';

interface MoodCheckInModalProps {
  isOpen: boolean;
  onClose: () => void;
  checkInType: 'before_learning' | 'after_learning' | 'during_break';
  onSubmit: (data: MoodCheckInData) => Promise<void>;
}

export interface MoodCheckInData {
  check_in_type: string;
  mood: string;
  mood_emoji: string;
  energy_level: number;
  stress_level: number;
  feeling_description?: string;
  what_went_well?: string;
  what_was_hard?: string;
  is_tired: boolean;
  is_hungry: boolean;
  is_distracted: boolean;
}

const MOODS = [
  { value: 'great', emoji: '😊', label: '매우 좋음' },
  { value: 'good', emoji: '🙂', label: '좋음' },
  { value: 'okay', emoji: '😐', label: '보통' },
  { value: 'struggling', emoji: '😔', label: '힘듦' },
  { value: 'frustrated', emoji: '😫', label: '좌절스러움' },
  { value: 'exhausted', emoji: '😩', label: '지침' },
];

export function MoodCheckInModal({
  isOpen,
  onClose,
  checkInType,
  onSubmit
}: MoodCheckInModalProps) {
  const [mood, setMood] = useState('');
  const [energyLevel, setEnergyLevel] = useState(5);
  const [stressLevel, setStressLevel] = useState(5);
  const [feelingDescription, setFeelingDescription] = useState('');
  const [whatWentWell, setWhatWentWell] = useState('');
  const [whatWasHard, setWhatWasHard] = useState('');
  const [isTired, setIsTired] = useState(false);
  const [isHungry, setIsHungry] = useState(false);
  const [isDistracted, setIsDistracted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!mood) {
      toast.error('기분을 선택해주세요!');
      return;
    }

    setIsSubmitting(true);

    try {
      const selectedMood = MOODS.find(m => m.value === mood);
      
      await onSubmit({
        check_in_type: checkInType,
        mood,
        mood_emoji: selectedMood?.emoji || '😐',
        energy_level: energyLevel,
        stress_level: stressLevel,
        feeling_description: feelingDescription || undefined,
        what_went_well: whatWentWell || undefined,
        what_was_hard: whatWasHard || undefined,
        is_tired: isTired,
        is_hungry: isHungry,
        is_distracted: isDistracted
      });

      // 초기화 및 닫기
      resetForm();
      onClose();
      toast.success('기분 체크인이 완료되었습니다! 💙');
    } catch (error) {
      console.error('기분 체크인 실패:', error);
      toast.error('기분 체크인에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setMood('');
    setEnergyLevel(5);
    setStressLevel(5);
    setFeelingDescription('');
    setWhatWentWell('');
    setWhatWasHard('');
    setIsTired(false);
    setIsHungry(false);
    setIsDistracted(false);
  };

  const getTitle = () => {
    switch (checkInType) {
      case 'before_learning':
        return '학습 시작 전 기분 체크인 ✨';
      case 'after_learning':
        return '학습 마무리 기분 체크인 🎉';
      case 'during_break':
        return '휴식 중 기분 체크인 ☕';
      default:
        return '기분 체크인';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">{getTitle()}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* 기분 선택 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              지금 기분이 어떠신가요?
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {MOODS.map((m) => (
                <button
                  key={m.value}
                  type="button"
                  onClick={() => setMood(m.value)}
                  className={`p-4 rounded-lg border-2 transition ${
                    mood === m.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="text-3xl mb-1">{m.emoji}</div>
                  <div className="text-sm font-medium text-gray-700">{m.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* 에너지 레벨 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              에너지 레벨: {energyLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={energyLevel}
              onChange={(e) => setEnergyLevel(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>매우 피곤함</span>
              <span>매우 활기참</span>
            </div>
          </div>

          {/* 스트레스 레벨 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              스트레스 레벨: {stressLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={stressLevel}
              onChange={(e) => setStressLevel(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>편안함</span>
              <span>매우 스트레스</span>
            </div>
          </div>

          {/* 신체 상태 체크박스 */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              신체 상태 (선택적)
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={isTired}
                  onChange={(e) => setIsTired(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-gray-700">😴 피곤해요</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={isHungry}
                  onChange={(e) => setIsHungry(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-gray-700">🍽️ 배고파요</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={isDistracted}
                  onChange={(e) => setIsDistracted(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-gray-700">📱 집중이 안 돼요</span>
              </label>
            </div>
          </div>

          {/* 감정 설명 (선택) */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              자세한 기분 설명 (선택)
            </label>
            <textarea
              value={feelingDescription}
              onChange={(e) => setFeelingDescription(e.target.value)}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="지금 느끼는 감정을 자유롭게 적어보세요..."
            />
          </div>

          {/* 학습 후 체크인인 경우 추가 질문 */}
          {checkInType === 'after_learning' && (
            <>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  오늘 잘한 점 💙
                </label>
                <textarea
                  value={whatWentWell}
                  onChange={(e) => setWhatWentWell(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="오늘 학습에서 잘한 점을 적어보세요..."
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  어려웠던 점 💛
                </label>
                <textarea
                  value={whatWasHard}
                  onChange={(e) => setWhatWasHard(e.target.value)}
                  rows={2}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="어려웠던 점이나 고민이 있다면 적어보세요..."
                />
              </div>
            </>
          )}

          {/* Submit 버튼 */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition"
              disabled={isSubmitting}
            >
              취소
            </button>
            <button
              type="submit"
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
              disabled={isSubmitting || !mood}
            >
              {isSubmitting ? '저장 중...' : '체크인 완료'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

