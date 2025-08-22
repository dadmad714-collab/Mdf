import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { BarChart3, Calculator, FileText, TrendingUp, Factory, DollarSign, Users, Target, Plus, Edit, Trash2, Eye, Download } from "lucide-react";
import { Toaster } from "./components/ui/toaster";
import { useToast } from "./hooks/use-toast";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newProjectName, setNewProjectName] = useState("");
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);
  const { toast } = useToast();

  const fetchProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      toast({
        title: "خطأ",
        description: "فشل في تحميل المشاريع",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProjectName.trim()) {
      toast({
        title: "خطأ",
        description: "يرجى إدخال اسم المشروع",
        variant: "destructive",
      });
      return;
    }

    try {
      await axios.post(`${API}/projects`, { project_name: newProjectName });
      setNewProjectName("");
      setShowCreateDialog(false);
      fetchProjects();
      toast({
        title: "نجح العملية",
        description: "تم إنشاء المشروع بنجاح",
      });
    } catch (error) {
      toast({
        title: "خطأ",
        description: "فشل في إنشاء المشروع",
        variant: "destructive",
      });
    }
  };

  const downloadReport = async (projectId, projectName) => {
    try {
      const response = await axios.get(`${API}/projects/${projectId}/report`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `تقرير_دراسة_الجدوى_${projectName}.pdf`;
      link.click();
      window.URL.revokeObjectURL(url);
      
      toast({
        title: "نجح العملية",
        description: "تم تحميل التقرير بنجاح",
      });
    } catch (error) {
      toast({
        title: "خطأ",
        description: "فشل في تحميل التقرير",
        variant: "destructive",
      });
    }
  };
    if (!window.confirm("هل أنت متأكد من حذف هذا المشروع؟ هذا الإجراء لا يمكن التراجع عنه.")) {
      return;
    }
    
    try {
      await axios.delete(`${API}/projects/${projectId}`);
      fetchProjects();
      toast({
        title: "نجح العملية",
        description: "تم حذف المشروع بنجاح",
      });
    } catch (error) {
      toast({
        title: "خطأ",
        description: "فشل في حذف المشروع",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto mb-4"></div>
          <p className="text-emerald-700 font-medium">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50" dir="rtl">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-emerald-200/50 sticky top-0 z-40">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4 space-x-reverse">
              <div className="bg-emerald-600 rounded-xl p-2">
                <Factory className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-emerald-900">دراسة الجدوى المتقدمة</h1>
                <p className="text-emerald-600 text-sm">مصنع ألواح MDF من سعف النخيل</p>
              </div>
            </div>
            
            <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
              <DialogTrigger asChild>
                <Button className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-2 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200">
                  <Plus className="h-4 w-4 ml-2" />
                  مشروع جديد
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]" dir="rtl">
                <DialogHeader>
                  <DialogTitle>إنشاء مشروع جديد</DialogTitle>
                  <DialogDescription>
                    أدخل اسم المشروع لبدء دراسة جدوى جديدة
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="projectName">اسم المشروع</Label>
                    <Input
                      id="projectName"
                      value={newProjectName}
                      onChange={(e) => setNewProjectName(e.target.value)}
                      placeholder="مثال: مصنع ألواح MDF - الرياض"
                      className="text-right"
                    />
                  </div>
                </div>
                <div className="flex justify-end space-x-2 space-x-reverse">
                  <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                    إلغاء
                  </Button>
                  <Button onClick={createProject} className="bg-emerald-600 hover:bg-emerald-700">
                    إنشاء المشروع
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {projects.length === 0 ? (
          <div className="text-center py-16">
            <div className="bg-white rounded-3xl p-12 shadow-xl border border-emerald-100 max-w-md mx-auto">
              <div className="bg-emerald-100 rounded-full p-4 w-20 h-20 mx-auto mb-6">
                <Factory className="h-12 w-12 text-emerald-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">لا توجد مشاريع بعد</h3>
              <p className="text-gray-600 mb-6">ابدأ بإنشاء مشروع جديد لدراسة جدوى مصنع ألواح MDF</p>
              <Button 
                onClick={() => setShowCreateDialog(true)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transition-all duration-200"
              >
                <Plus className="h-4 w-4 ml-2" />
                إنشاء مشروع جديد
              </Button>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <Card key={project.id} className="bg-white/70 backdrop-blur-sm border-emerald-200 hover:shadow-2xl transition-all duration-300 rounded-2xl overflow-hidden group">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg font-semibold text-emerald-900 group-hover:text-emerald-700 transition-colors">
                      {project.project_name}
                    </CardTitle>
                    <Badge variant={project.is_completed ? "default" : "secondary"} className="text-xs">
                      {project.is_completed ? "مكتمل" : "قيد التنفيذ"}
                    </Badge>
                  </div>
                  <CardDescription className="text-emerald-600">
                    تم الإنشاء: {new Date(project.created_at).toLocaleDateString('ar-SA')}
                  </CardDescription>
                </CardHeader>
                
                <CardContent className="space-y-4">
                  {/* Progress Indicators */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">البيانات المالية</span>
                      <div className="flex items-center space-x-2 space-x-reverse">
                        <DollarSign className="h-4 w-4 text-emerald-600" />
                        <Badge variant={project.financial_data ? "default" : "outline"} className="text-xs">
                          {project.financial_data ? "مكتمل" : "غير مكتمل"}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">البيانات الفنية</span>
                      <div className="flex items-center space-x-2 space-x-reverse">
                        <Factory className="h-4 w-4 text-blue-600" />
                        <Badge variant={project.technical_data ? "default" : "outline"} className="text-xs">
                          {project.technical_data ? "مكتمل" : "غير مكتمل"}
                        </Badge>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">بيانات السوق</span>
                      <div className="flex items-center space-x-2 space-x-reverse">
                        <TrendingUp className="h-4 w-4 text-purple-600" />
                        <Badge variant={project.market_data ? "default" : "outline"} className="text-xs">
                          {project.market_data ? "مكتمل" : "غير مكتمل"}
                        </Badge>
                      </div>
                    </div>
                  </div>

                  {/* Financial Results Preview */}
                  {project.financial_results && (
                    <div className="bg-emerald-50 rounded-xl p-4 space-y-3">
                      <div className="text-center mb-3">
                        <Badge 
                          variant={project.financial_results.is_feasible ? "default" : "destructive"}
                          className="text-sm font-bold px-4 py-1"
                        >
                          {project.financial_results.is_feasible ? "مجدي اقتصادياً ✅" : "غير مجدي اقتصادياً ❌"}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div className="bg-white/60 rounded-lg p-2">
                          <div className="text-xs text-emerald-600 mb-1">صافي القيمة الحالية</div>
                          <div className="font-bold text-emerald-900">
                            {(project.financial_results.npv / 1000000).toFixed(1)} مليون ريال
                          </div>
                        </div>
                        
                        <div className="bg-white/60 rounded-lg p-2">
                          <div className="text-xs text-emerald-600 mb-1">معدل العائد الداخلي</div>
                          <div className="font-bold text-emerald-900">
                            {project.financial_results.irr.toFixed(1)}%
                          </div>
                        </div>
                        
                        <div className="bg-white/60 rounded-lg p-2">
                          <div className="text-xs text-emerald-600 mb-1">فترة الاسترداد</div>
                          <div className="font-bold text-emerald-900">
                            {project.financial_results.payback_period.toFixed(1)} سنة
                          </div>
                        </div>
                        
                        <div className="bg-white/60 rounded-lg p-2">
                          <div className="text-xs text-emerald-600 mb-1">العائد على الاستثمار</div>
                          <div className="font-bold text-emerald-900">
                            {project.financial_results.roi.toFixed(1)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex space-x-2 space-x-reverse pt-4 border-t border-emerald-100">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedProject(project)}
                      className="flex-1 hover:bg-emerald-50 hover:border-emerald-300"
                    >
                      <Eye className="h-4 w-4 ml-1" />
                      عرض
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedProject(project)}
                      className="flex-1 hover:bg-blue-50 hover:border-blue-300"
                    >
                      <Edit className="h-4 w-4 ml-1" />
                      تعديل
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => deleteProject(project.id)}
                      className="hover:bg-red-50 hover:border-red-300 hover:text-red-600"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>

      {/* Project Details/Edit Modal */}
      {selectedProject && (
        <ProjectModal
          project={selectedProject}
          onClose={() => setSelectedProject(null)}
          onUpdate={fetchProjects}
        />
      )}
    </div>
  );
};

const ProjectModal = ({ project, onClose, onUpdate }) => {
  const [activeTab, setActiveTab] = useState("financial");
  const [financialData, setFinancialData] = useState(project.financial_data || {});
  const [technicalData, setTechnicalData] = useState(project.technical_data || {});
  const [marketData, setMarketData] = useState(project.market_data || {});
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const updateProject = async () => {
    setLoading(true);
    try {
      await axios.put(`${API}/projects/${project.id}`, {
        financial_data: financialData,
        technical_data: technicalData,
        market_data: marketData,
      });
      
      toast({
        title: "نجح العملية",
        description: "تم تحديث المشروع بنجاح",
      });
      onUpdate();
      onClose();
    } catch (error) {
      toast({
        title: "خطأ",
        description: "فشل في تحديث المشروع",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="max-w-5xl max-h-[95vh] overflow-y-auto" dir="rtl">
        <DialogHeader className="sticky top-0 bg-white z-10 pb-4 border-b">
          <DialogTitle className="text-xl font-bold text-emerald-900">
            {project.project_name}
          </DialogTitle>
          <DialogDescription>
            تحديث بيانات دراسة الجدوى
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-6 h-12 bg-emerald-50">
              <TabsTrigger 
                value="financial" 
                className="flex items-center text-sm font-medium py-3 data-[state=active]:bg-emerald-600 data-[state=active]:text-white"
              >
                <DollarSign className="h-4 w-4 ml-1" />
                البيانات المالية
              </TabsTrigger>
              <TabsTrigger 
                value="technical" 
                className="flex items-center text-sm font-medium py-3 data-[state=active]:bg-blue-600 data-[state=active]:text-white"
              >
                <Factory className="h-4 w-4 ml-1" />
                البيانات الفنية
              </TabsTrigger>
              <TabsTrigger 
                value="market" 
                className="flex items-center text-sm font-medium py-3 data-[state=active]:bg-purple-600 data-[state=active]:text-white"
              >
                <TrendingUp className="h-4 w-4 ml-1" />
                بيانات السوق
              </TabsTrigger>
            </TabsList>

          <TabsContent value="financial" className="space-y-6 mt-6">
            <FinancialDataForm data={financialData} onChange={setFinancialData} />
          </TabsContent>

          <TabsContent value="technical" className="space-y-6 mt-6">
            <TechnicalDataForm data={technicalData} onChange={setTechnicalData} />
          </TabsContent>

          <TabsContent value="market" className="space-y-6 mt-6">
            <MarketDataForm data={marketData} onChange={setMarketData} />
          </TabsContent>
          </Tabs>
        </div>

        <div className="flex justify-end space-x-2 space-x-reverse pt-6 border-t bg-white sticky bottom-0">
          <Button variant="outline" onClick={onClose}>
            إلغاء
          </Button>
          <Button 
            onClick={updateProject} 
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-700"
          >
            {loading ? "جاري الحفظ..." : "حفظ التغييرات"}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

const FinancialDataForm = ({ data, onChange }) => {
  const updateField = (field, value) => {
    onChange({ ...data, [field]: parseFloat(value) || 0 });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-emerald-800">تكاليف الاستثمار الأولي</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="land_cost">تكلفة الأرض (ريال)</Label>
            <Input
              id="land_cost"
              type="number"
              value={data.land_cost || ""}
              onChange={(e) => updateField("land_cost", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="building_construction">تكلفة البناء (ريال)</Label>
            <Input
              id="building_construction"
              type="number"
              value={data.building_construction || ""}
              onChange={(e) => updateField("building_construction", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="machinery_equipment">المعدات والآلات (ريال)</Label>
            <Input
              id="machinery_equipment"
              type="number"
              value={data.machinery_equipment || ""}
              onChange={(e) => updateField("machinery_equipment", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="installation_cost">تكلفة التركيب (ريال)</Label>
            <Input
              id="installation_cost"
              type="number"
              value={data.installation_cost || ""}
              onChange={(e) => updateField("installation_cost", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="pre_operational_expenses">مصاريف ما قبل التشغيل (ريال)</Label>
            <Input
              id="pre_operational_expenses"
              type="number"
              value={data.pre_operational_expenses || ""}
              onChange={(e) => updateField("pre_operational_expenses", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="working_capital">رأس المال العامل (ريال)</Label>
            <Input
              id="working_capital"
              type="number"
              value={data.working_capital || ""}
              onChange={(e) => updateField("working_capital", e.target.value)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-emerald-800">تكاليف المواد الخام</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="palm_fronds_cost_per_ton">تكلفة سعف النخيل (ريال/طن)</Label>
            <Input
              id="palm_fronds_cost_per_ton"
              type="number"
              value={data.palm_fronds_cost_per_ton || ""}
              onChange={(e) => updateField("palm_fronds_cost_per_ton", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="adhesive_cost">تكلفة المواد اللاصقة (ريال)</Label>
            <Input
              id="adhesive_cost"
              type="number"
              value={data.adhesive_cost || ""}
              onChange={(e) => updateField("adhesive_cost", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="chemicals_cost">تكلفة المواد الكيميائية (ريال)</Label>
            <Input
              id="chemicals_cost"
              type="number"
              value={data.chemicals_cost || ""}
              onChange={(e) => updateField("chemicals_cost", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="energy_cost_per_unit">تكلفة الطاقة (ريال/وحدة)</Label>
            <Input
              id="energy_cost_per_unit"
              type="number"
              value={data.energy_cost_per_unit || ""}
              onChange={(e) => updateField("energy_cost_per_unit", e.target.value)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-emerald-800">التكاليف التشغيلية الشهرية</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="labor_cost_monthly">تكلفة العمالة (ريال/شهر)</Label>
            <Input
              id="labor_cost_monthly"
              type="number"
              value={data.labor_cost_monthly || ""}
              onChange={(e) => updateField("labor_cost_monthly", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="maintenance_cost_monthly">تكلفة الصيانة (ريال/شهر)</Label>
            <Input
              id="maintenance_cost_monthly"
              type="number"
              value={data.maintenance_cost_monthly || ""}
              onChange={(e) => updateField("maintenance_cost_monthly", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="utilities_cost_monthly">المرافق (كهرباء، ماء) (ريال/شهر)</Label>
            <Input
              id="utilities_cost_monthly"
              type="number"
              value={data.utilities_cost_monthly || ""}
              onChange={(e) => updateField("utilities_cost_monthly", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="administrative_cost_monthly">التكاليف الإدارية (ريال/شهر)</Label>
            <Input
              id="administrative_cost_monthly"
              type="number"
              value={data.administrative_cost_monthly || ""}
              onChange={(e) => updateField("administrative_cost_monthly", e.target.value)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-emerald-800">بيانات الإيرادات</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="mdf_price_per_cubic_meter">سعر بيع MDF (ريال/متر مكعب)</Label>
            <Input
              id="mdf_price_per_cubic_meter"
              type="number"
              value={data.mdf_price_per_cubic_meter || ""}
              onChange={(e) => updateField("mdf_price_per_cubic_meter", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="production_capacity_monthly">الطاقة الإنتاجية (متر مكعب/شهر)</Label>
            <Input
              id="production_capacity_monthly"
              type="number"
              value={data.production_capacity_monthly || ""}
              onChange={(e) => updateField("production_capacity_monthly", e.target.value)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-emerald-800">المعايير المالية</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <Label htmlFor="project_life_years">عمر المشروع (سنوات)</Label>
            <Input
              id="project_life_years"
              type="number"
              value={data.project_life_years || 10}
              onChange={(e) => updateField("project_life_years", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="discount_rate">معدل الخصم (%)</Label>
            <Input
              id="discount_rate"
              type="number"
              step="0.1"
              value={data.discount_rate || 10}
              onChange={(e) => updateField("discount_rate", e.target.value)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="tax_rate">معدل الضريبة (%)</Label>
            <Input
              id="tax_rate"
              type="number"
              step="0.1"
              value={data.tax_rate || 15}
              onChange={(e) => updateField("tax_rate", e.target.value)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const TechnicalDataForm = ({ data, onChange }) => {
  const updateField = (field, value) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-blue-800">مواصفات الإنتاج</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="daily_production_capacity">الطاقة الإنتاجية اليومية (متر مكعب)</Label>
            <Input
              id="daily_production_capacity"
              type="number"
              value={data.daily_production_capacity || ""}
              onChange={(e) => updateField("daily_production_capacity", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="working_days_per_month">أيام العمل الشهرية</Label>
            <Input
              id="working_days_per_month"
              type="number"
              value={data.working_days_per_month || 26}
              onChange={(e) => updateField("working_days_per_month", parseInt(e.target.value) || 26)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="palm_fronds_requirement_per_cubic_meter">احتياج سعف النخيل (طن/متر مكعب)</Label>
            <Input
              id="palm_fronds_requirement_per_cubic_meter"
              type="number"
              step="0.1"
              value={data.palm_fronds_requirement_per_cubic_meter || ""}
              onChange={(e) => updateField("palm_fronds_requirement_per_cubic_meter", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-blue-800">المتطلبات الفنية</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="factory_area_required">المساحة المطلوبة (متر مربع)</Label>
            <Input
              id="factory_area_required"
              type="number"
              value={data.factory_area_required || ""}
              onChange={(e) => updateField("factory_area_required", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="electricity_requirement_kw">الطاقة الكهربائية المطلوبة (كيلو واط)</Label>
            <Input
              id="electricity_requirement_kw"
              type="number"
              value={data.electricity_requirement_kw || ""}
              onChange={(e) => updateField("electricity_requirement_kw", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="water_requirement_daily">الاستهلاك اليومي للماء (لتر)</Label>
            <Input
              id="water_requirement_daily"
              type="number"
              value={data.water_requirement_daily || ""}
              onChange={(e) => updateField("water_requirement_daily", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="labor_requirement">عدد العمال المطلوب</Label>
            <Input
              id="labor_requirement"
              type="number"
              value={data.labor_requirement || ""}
              onChange={(e) => updateField("labor_requirement", parseInt(e.target.value) || 0)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const MarketDataForm = ({ data, onChange }) => {
  const updateField = (field, value) => {
    onChange({ ...data, [field]: value });
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-purple-800">تحليل السوق</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="target_market_size">حجم السوق المستهدف (ريال)</Label>
            <Input
              id="target_market_size"
              type="number"
              value={data.target_market_size || ""}
              onChange={(e) => updateField("target_market_size", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="market_growth_rate">معدل نمو السوق (%)</Label>
            <Input
              id="market_growth_rate"
              type="number"
              step="0.1"
              value={data.market_growth_rate || ""}
              onChange={(e) => updateField("market_growth_rate", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="market_share_target">الحصة السوقية المستهدفة (%)</Label>
            <Input
              id="market_share_target"
              type="number"
              step="0.1"
              value={data.market_share_target || ""}
              onChange={(e) => updateField("market_share_target", parseFloat(e.target.value) || 0)}
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="pricing_strategy">استراتيجية التسعير</Label>
            <Input
              id="pricing_strategy"
              value={data.pricing_strategy || ""}
              onChange={(e) => updateField("pricing_strategy", e.target.value)}
              placeholder="مثال: تسعير تنافسي"
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg text-purple-800">المخاطر السوقية</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="demand_seasonality">موسمية الطلب</Label>
            <Input
              id="demand_seasonality"
              value={data.demand_seasonality || ""}
              onChange={(e) => updateField("demand_seasonality", e.target.value)}
              placeholder="مثال: مستقر على مدار السنة"
              className="text-right"
            />
          </div>
          <div>
            <Label htmlFor="competition_level">مستوى المنافسة</Label>
            <Input
              id="competition_level"
              value={data.competition_level || "متوسط"}
              onChange={(e) => updateField("competition_level", e.target.value)}
              className="text-right"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
        </Routes>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;